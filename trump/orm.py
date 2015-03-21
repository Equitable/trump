# -*- coding: utf-8 -*-
"""
Trump's Object Relational Model is the glue to the framework, used to creat 
a Symbol's tags, alias, meta data, data feeds and their sources, munging and validity
instructions.
"""

#SQLAQ - running the uninstall script, then this script, in the same session
#        causes an error:
#
#        sqlalchemy.exc.InvalidRequestError: When initializing mapper 
#        Mapper|Feed|_feeds, expression 'FeedMeta' failed to locate a name 
#        ("name 'FeedMeta' is not defined"). If this is a class name, consider
#        adding this relationship() to the <class 'trump.orm.Feed'> class
#        after both dependent classes have been defined
#
#        Why?

import pandas as pd
import datetime as dt

from sqlalchemy import event, Table, Column, ForeignKey, ForeignKeyConstraint,\
                       String, Integer, Float, DateTime, MetaData, \
                       func

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import object_session

from sqlalchemy.exc import ProgrammingError

from sqlalchemy.sql.expression import insert, delete
from sqlalchemy.sql import and_

from tools import ReprMixin, ProxyDict, isinstanceofany
from sqlalchemy import create_engine

from extensions.symbol_aggs import apply_row, choose_col
from extensions.feed_munging import munging_methods

from templating import bFeed
from templating import pab, pnab

from options import read_config, read_settings

engine_str = read_config('readwrite')['engine']
engine = create_engine(engine_str)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

metadata = MetaData(bind=engine)

cc = {'onupdate' : "CASCADE", 'ondelete' : "CASCADE"}
      
checkpoints = ('EXCEPTION','CHECK')
state = ('ENABLED','DISABLED','ERROR')

class SymbolManager(object):
    """
    A SymbolManager handles the creation, getting and deletion of symbols.
    """
    def __init__(self,ses=session):
        self.ses = session
    def create(self,name,description=None,freq=None,units=None,agg_method="PRIORITY_FILL"):
        """
        Create, or gets if exists, a Symbol.
        """
        sym = self.try_to_get(name)
        if sym is not None:
            print sym.name
            self.ses.delete(sym)
            self.ses.commit() 
        sym = Symbol(name,description,freq,units,agg_method)
        sym.addAlias(name)
        return sym      
    def delete(self,symbol):
        """
        Deletes a Symbol.
        """
        if isinstance(symbol,str):
            sym = self.get(symbol)
        elif isinstance(symbol,Symbol):
            sym = symbol
        del sym
        self.ses.commit()
    def complete(self):
        self.ses.commit()
    def exists(self,symbol):
        syms = self.ses.query(Symbol).filter(Symbol.name == symbol).all()
        if len(syms) == 0:
            return False
        else:
            return True
    def get(self,symbol):
        """
        Gets a Symbol based on name, which is expected to exist. Errors if it doesn't exist.
        
        #TODO enable alias use.
        """
        syms = self.try_to_get(symbol)
        if syms == None:
            raise Exception("Symbol {} does not exist".format(symbol))
        else:
            return syms
    def try_to_get(self,symbol):
        syms = self.ses.query(Symbol).filter(Symbol.name == symbol).all()
        if len(syms) == 0:
            return None
        else:
            return syms[0]    

class Symbol(Base, ReprMixin): 
    """
    agg_method : see extensions.symbol_aggs.py and look at the wrapped function names.
    """
    __tablename__ = '_symbols'
    
    name =        Column('name',String,primary_key = True)
    description = Column('description',String)
    freq =        Column('freq',String)
    units =       Column('units',String)
    agg_method =  Column('agg_method',String)
    
    tags =        relationship("SymbolTag",cascade="all, delete-orphan")
    aliases =     relationship("SymbolAlias",cascade="all, delete-orphan")
    validity =    relationship("SymbolValidity",cascade="all, delete-orphan")
    feeds =       relationship("Feed",cascade="all, delete-orphan")
    
    #overrides =   relationship("Override",cascade="save-update",passive_deletes=True)
    
    def __init__(self,name,description=None,freq=None,units=None,agg_method="PRIORITY_FILL"):
        """
        agg_method : see extensions.symbol_aggs.py
        
        """         
        self.name = name
        self.description = description
        self.freq = freq
        self.units = units
        self.agg_method = agg_method
        self.datatable = None
        self.datatable_exists = False
        #SQLAQ - Is this okay to do? It feels sneaky, dirty and wrong.
        session.add(self)
        
    def cache_feed(self,fid):
        raise NotImplemented
    def cache(self):
        """
        Re-caches the Symbol's datatable by quering each Feed.
        """
        
        data = []
        cols = ['final','override_feed000','failsafe_feed999']
        
        #TODO : Take out the override columns.  That behavious should be
        #       Extension agnostic.
        
        for f in self.feeds:
            f.cache()
            data.append(f.data)
            cols.append(f.data.name)
        
        
        data = pd.concat(data,axis=1)
        
        l = len(data)
        data['override_feed000'] = [None] * l
        data['failsafe_feed999'] = [None] * l

        os = object_session(self)
        
        gb = os.query(Override.dt_ind,func.max(Override.dt_log).label('max_dt_log')).group_by(Override.dt_ind).subquery()
        ords = os.query(Override).join((gb, and_(Override.dt_ind == gb.c.dt_ind, Override.dt_log == gb.c.max_dt_log))).all()
              
        for row in ords:
            data.loc[row.dt_ind,'override_feed000'] = row.value

        gb = os.query(FailSafe.dt_ind,func.max(FailSafe.dt_log).label('max_dt_log')).group_by(FailSafe.dt_ind).subquery()
        ords = os.query(FailSafe).join((gb, and_(FailSafe.dt_ind == gb.c.dt_ind, FailSafe.dt_log == gb.c.max_dt_log))).all()
              
        for row in ords:
            data.loc[row.dt_ind,'failsafe_feed999'] = row.value
            
        print data
        print self.agg_method
        print apply_row

        if self.agg_method in apply_row:
            data['final'] = data.apply(apply_row[self.agg_method],axis=1)
        elif self.agg_method in choose_col:
            data['final'] = choose_col[self.agg_method](data)
        
        # SQLAQ There are several states to deal with at this point
        # A) the datatable exists but a feed has been added
        # B) the datatable doesn't exist and needs to be created
        # C) the datatable needs to be updated for more or less feeds
        # D) the datatable_exists flag is incorrect because all edge cases
        #    haven't been handled yet.
        #
        # My logic is that once Trump is more functional, I'll be able to 
        # eliminate this hacky solution.  But, SQLAlchemy might have 
        # a more elegant answer.  A check, of somekind prior to deletion?
         
        # if not self.datatable_exists:
        #     self.InitializeDataTable()
        # delete(self.datatable).execute()
        # self.InitializeDataTable()
         
        # Is this the best way to check?
        if engine.dialect.has_table(session.connection(), self.name):
            delete(self.datatable).execute()
        self.InitializeDataTable()
                  
        for index, row in data.iterrows():
            vals = {k : row[k] for k in cols}
            vals['datetime'] = index
            insert(self.datatable,vals).execute()
          
                
    @property
    def describe(self):
        """
        Describes a Symbol
        
        #TODO Check/test/improve.
        #TODO Create a Feed's describe() to Feed, and use it here.
        """
        s = []
        s.append("Symbol = {}".format(self.name))
        if len(self.tags):
            s.append("  tagged = {}".format(", ".join(x.tag for x in self.tags)))
        if len(self.aliases):
            s.append("  aliased = {}".format(", ".join(x.alias for x in self.aliases)))
        if len(self.validity):
            s.append("  validity =")
            printed_cp = []
            for v in self.validity:
                if v.checkpoint not in printed_cp:
                    printed_cp.append(v.checkpoint)
                    s.append("    Checkpoint = {}".format(v.checkpoint))
                s.append("      {} -> {} : {}".format(v.logic,v.key,v.value))
        if len(self.feeds):
            s.append("  feeds:")
        
            for f in self.feeds:
                s.append("    {}. {} -> {}".format(f.fnum,f.ftype,f.source_str()))
                printed_cp = []
                for v in f.validity:
                    if v.checkpoint not in printed_cp:
                        printed_cp.append(v.checkpoint)
                        s.append("      Checkpoint = {}".format(v.checkpoint))
                    s.append("        {} -> {} : {}".format(v.logic,v.key,v.value))        
        return "\n".join(s)
                  
    def addTag(self,tag):
        # SQLA Adding a SymbolTag object, feels awkward/uneccessary.
        # Should I be implementing this functionality a different way?
        os = object_session(self)
        tmp = SymbolTag(tag=tag,symbol=self)
        self.tags.append(tmp)
        os.add(tmp)
        os.commit()
   
    def addOverride(self,dt_ind,value,dt_log=None,user=None,comment=None):
        os = object_session(self)
        
        if not dt_log:
            dt_log = dt.datetime.now()
            
        tmp = Override(symname=self.name,dt_ind=dt_ind,value=value,dt_log=dt_log,user=user,comment=comment)
        os.add(tmp)
        os.commit()

    def addFailSafe(self,dt_ind,value,dt_log=None,user=None,comment=None):
        os = object_session(self)
        
        if not dt_log:
            dt_log = dt.datetime.now()
            
        tmp = FailSafe(symname=self.name,dt_ind=dt_ind,value=value,dt_log=dt_log,user=user,comment=comment)
        os.add(tmp)
        os.commit()
        
    def delTag(self):
        raise NotImplemented
        
    def addTags(self,tags):
        os = object_session(self)        
        tmps = [SymbolTag(tag=t,symbol=self) for t in tags]
        os.add_all(tmps)
        os.commit()
    
    @property
    def n_tags(self):
        return len(self.tags)

    def addFeed(self,obj,**kwargs):
        if 'fnum' in kwargs:
            fnum = kwargs['fnum']
            del kwargs['fnum']
        else:
            fnum = None
            
        if isinstance(obj,bFeed):
            munging = obj.munging
            if 'munging' in kwargs:
                explicit_munging = kwargs['munging'].as_odict
                for key in explicit_munging:
                    munging[key] = explicit_munging[key]                   
            f = Feed(self,obj.ftype,obj.sourcing,munging,obj.validity,obj.meta,fnum)
        if isinstance(obj,Feed):
            f = obj
        self.feeds.append(f)
        session.add(f)
    def addAlias(self,obj):
        if isinstance(obj,list):
            raise NotImplemented
        elif isinstanceofany(obj,(str,unicode)):
            a = SymbolAlias(self,obj)
            self.aliases.append(a)
            session.add(a)             
    def data(self):
        t = self.datatable
        return session.query(t.c.datetime,t.c.final).all()
    @property
    def df(self):
        data = self.data()
        df = pd.DataFrame(data)           
        df.columns = ['dateindex',self.name]
        df = df.set_index('dateindex')
        return df
    def delFeed(self):
        raise NotImplemented

    def addFeeds(self,symbol,ftype,sourcing,munging=None,fnum=None):
        raise NotImplemented
        
    @property
    def n_feeds(self):
        return len(self.feeds)

    def addValidity(self,checkpoint,logic,kwargs):
        for key,value in kwargs.iteritems():
            self.validity.append(SymbolValidity(checkpoint=checkpoint,logic=logic,key=key,value=value,symbol=self))
        #self = session.merge(self)
        session.commit()
        
    def setDescription(self,description):
        self.description = description

    def setFreq(self,freq):
        self.freq = freq
        
    def setUnits(self,units):
        self.units = units
        
    def InitializeDataTable(self):
        self.datatable = self._DataTableFactory()
        self.datatable.create(checkfirst=True)
        self.datatable_exists = True
        
    def _DataTableFactory(self):
        feed_cols = ['feed{0:03d}'.format(i+1) for i in range(self.n_feeds)]
        feed_cols = ['override_feed000'] + feed_cols + ['failsafe_feed999']
        
        t = Table(self.name, metadata, 
                  Column('datetime', DateTime, primary_key=True),
                  Column('final', Float),
                  *(Column(feed_col, Float) for feed_col in feed_cols),
                  extend_existing=True)
        return t

@event.listens_for(Symbol, 'load')
def __receive_load(target, context):
    target.InitializeDataTable()
    
class SymbolTag(Base, ReprMixin):
    __tablename__ = '_symbol_tags'
    symname = Column('symname',String,ForeignKey('_symbols.name', **cc),  primary_key = True)
    tag =  Column('tag',String, primary_key = True)
    symbol = relationship("Symbol")
    def __init__(self,symbol,tag):
        self.symbol = symbol
        self.tag = tag

class SymbolAlias(Base, ReprMixin):
    __tablename__ = '_symbol_aliases'               
    symname = Column('symname',String,ForeignKey('_symbols.name', **cc), primary_key = True)
    alias = Column('alias',String, primary_key = True)
    
    symbol = relationship("Symbol")  
    def __init__(self,symbol,alias):
        self.symbol = symbol
        self.alias = alias

class SymbolValidity(Base, ReprMixin):
    __tablename__ = "_symbol_validity"
    
    symname = Column('symname', String, ForeignKey("_symbols.name", **cc), primary_key = True)
    checkpoint = Column('checkpoint',String, primary_key = True)
    logic = Column('logic',String, primary_key = True)
    key = Column('key',String, primary_key = True)
    value = Column('value',String)

    symbol = relationship("Symbol")   
    def __init__(self,symbol,checkpoint,logic,key,value=None):
        self.symbol = symbol
        self.checkpoint = checkpoint
        self.logic = logic
        self.key = key
        self.value = value

class Feed(Base, ReprMixin):
    __tablename__ = "_feeds"
    
    symname = Column('symname',String, ForeignKey("_symbols.name", **cc), primary_key = True)
    fnum = Column('fnum',Integer,primary_key = True)
       
    state = Column('state',String,nullable=False)
    ftype = Column('ftype',String,nullable=False)
    
    tags = relationship("FeedTag",cascade="all, delete-orphan")
    sourcing = relationship("FeedSource",lazy="dynamic",cascade="all, delete-orphan")
    meta = relationship("FeedMeta",lazy="dynamic",cascade="all, delete-orphan")
    munging = relationship("FeedMunge",lazy="dynamic",cascade="all, delete-orphan")
    validity = relationship("FeedValidity",lazy="dynamic",cascade="all, delete-orphan")
       
    symbol = relationship("Symbol")

    def __init__(self,symbol,ftype,sourcing,munging=None,validity=None,meta=None,fnum=None):
        self.ftype = ftype
        self.state = "ON"
        self.symbol = symbol
        self.data = None
        
        self._symsess = object_session(symbol)
        
        if fnum is None:
            existing_fnums = session.query(Feed.fnum).filter(Feed.symname == symbol.name).all()
            existing_fnums = [n[0] for n in existing_fnums]
            if len(existing_fnums) == 0:
                self.fnum = 0
            else:
                self.fnum = max(existing_fnums) + 1
        else:
            self.fnum = fnum
            
        def setinmeta(t,o):
            val = None
            if meta is not None and t in meta:
                val = meta[t]
                del meta[t]
            elif o is not None and t in o: #otherwise fall back to the value used in the sourcing dictionary.
                val = o[t]
                del o[t]
            
            if val:
                tmp = FeedMeta(attr=t,value=val,feed=self)
                self._symsess.add(tmp)
                self.meta_map[t] = tmp
                self._symsess.commit()
        
        setinmeta('stype',sourcing)
        setinmeta('sourcing_key',sourcing)
        setinmeta('vtype',validity)

        if meta:
            for key in meta:
                tmp = FeedMeta(attr=key,value=meta[key],feed=self)
                self._symsess.add(tmp)
                self.meta_map[key] = tmp
                self._symsess.commit()            
        
        if sourcing:        
            for key in sourcing:
                tmp = FeedSource(param=key,value=sourcing[key],feed=self)
                self._symsess.add(tmp)
                self.sourcing_map[key] = tmp
                self._symsess.commit()   

        if munging:            
            for i,meth in enumerate(munging.keys()):
                print i,meth, munging[meth]
                fm = FeedMunge(order=i,mtype=munging[meth]['mtype'],method=meth,feed=self)
                for arg,value in munging[meth]['kwargs'].iteritems():
                    print arg,value
                    # TODO making munging arguments dynamically typed
                    if not isinstance(value,(int,float)):
                        val = str(value)
                    else:
                        val = value
                    fm.mungeargs.append(FeedMungeArg(arg,val,feedmunge=fm))
                self.munging.append(fm)

        if validity:
            for checkpoint in validity:
                for logic in checkpoint:
                    for key in logic:
                        self.validity.append(FeedValidity(checkpoint,logic,key,logic[key]))
    def cache(self):
        
        # Pull in the database defined sourcing arguments
        # for now, this is a dictionary of the forms {str : str,}
        kwargs = self.sourcing_map()

        # Check the source type
        meta = self.meta_map()
        stype = meta['stype']
         
        # If there is a sourcing key defined, use it to override any database
        # defined parameters
        if 'sourcing_key' in meta:
            sourcing_key = meta['sourcing_key']
            sourcing_overrides = read_settings()[stype][sourcing_key]
            for key in sourcing_overrides:
                kwargs[key] = sourcing_overrides[key]

        # Depending on the feed type, use the kwargs appropriately to
        # populate a dataframe, self.data.
        if stype == 'Quandl':
            import Quandl as q
            self.data = q.get(**kwargs)
            self.data = self.data[kwargs['fieldname']]
        elif stype == 'psycopg2':
            import psycopg2 as db
            con_kwargs = {k:v for k,v in kwargs.items() if k in ['dsn','user','password','host','database','port']}
            con = db.connect(**con_kwargs)
            raise NotImplementedError("pyscopg2")
        elif stype == 'DBAPI':
            db = __import__(engine.driver)
            con_kwargs = {k:v for k,v in kwargs.items() if k in ['dsn','user','password','host','database','port']}

            print kwargs
            print con_kwargs
            
            con = db.connect(**con_kwargs) 
            cur = con.cursor()

            if 'command' in kwargs:
                cur.execute(kwargs['command'])
            elif set(['table','indexcol','datacol']).issubset(kwargs.keys()):
                
                i,d,t = kwargs['indexcol'],kwargs['datacol'],kwargs['table']
                qry = "SELECT {0},{1} FROM {2} ORDER BY {0};".format(i,d,t)
                cur.execute(qry)
                      
            results = [(row[0],row[1]) for row in cur.fetchall()]
            con.close()
            ind,dat = zip(*results)
            self.data = pd.Series(dat,ind)
        elif stype == 'SQLAlchemy':
            NotImplementedError("SQLAlchemy")
        elif stype == 'pydata':
            NotImplementedError("pydata")
        else:
            raise Exception("Unknown Source Type : {}".format(stype))

        #print self.data.tail(5)
        #print type(self.data)
        #print self.data.index
        #print self.data.dtype

       
        #munge accordingly
        for m in self.munging:
            print m.mtype
            mmkeys = m.munging_map.keys()
            kwargs = {k : m.munging_map[k].value for k in mmkeys}
            for arg in kwargs:
                #TODO handle types better.
                if kwargs[arg].isnumeric():
                    tmp = float(kwargs[arg])
                    if (tmp % 1) == 0: #then, probably an int.
                        kwargs[arg] = int(tmp)
                    else:
                        kwargs[arg] = tmp
                elif kwargs[arg].upper() == 'TRUE':
                    kwargs[arg] = True
                elif kwargs[arg].upper() == 'FALSE':
                    kwargs[arg] = False                   
            if m.mtype == pab:
                func = getattr(self.data,m.method)
                #print m.method, func
                #print kwargs
                #self.data['2015-03-16'] = pd.np.nan
                #print self.data.tail()
                #self.data = func() #TODO: add kwargs, test.
                self.data = func(**kwargs) #TODO: add kwargs, test.
                #print self.data.tail()
            elif m.mtype == pnab:
                lib = __import__('pandas',globals(),locals(),[],-1)
                func = getattr(lib,m.method)
                #print m.method, func
                #print kwargs
                self.data = func(self.data,**kwargs)
        
        #make sure it's named properly...
        self.data.name = "feed" + str(self.fnum+1).zfill(3)
        
#            for a in m.methodargs:
#                args[a.arg] = a.value
#            self.data = munging_methods[m.method](self.data,**args)

    @property
    def sourcing_map(self):
        return ProxyDict(self, 'sourcing', FeedSource, 'param')

    @property
    def meta_map(self):
        return ProxyDict(self, 'meta', FeedMeta, 'attr')
     
    @property         
    def source(self):
        return " ".join([p.key + " : " + p.value for p in self.sourcing])
               
class FeedTag(Base, ReprMixin):
    __tablename__ = '_feed_tags'
    symname = Column('symname',String,  primary_key = True)
    fnum = Column('fnum',Integer,  primary_key = True)
    
    tag =  Column('tag',String, primary_key = True)
    
    feed = relationship("Feed")

    __table_args__ = (ForeignKeyConstraint([symname,fnum],[Feed.symname,Feed.fnum], **cc),{})
         
class FeedSource(Base, ReprMixin):
    __tablename__ = "_feed_sourcing"
    
    symname = Column('symname',String, primary_key = True)
    fnum = Column('fnum',Integer, primary_key = True)
    param =  Column('param',String, primary_key = True)
    
    feed = relationship("Feed")
    
    value = Column('value',String)
    
    __table_args__ = (ForeignKeyConstraint([symname,fnum],[Feed.symname,Feed.fnum], **cc),{})
    def __init__(self,feed,param,value):
        self.feed = feed
        self.param = param
        self.value = value

class FeedMeta(Base, ReprMixin):
    __tablename__ = "_feed_meta"
    
    symname = Column('symname',String, primary_key = True)
    fnum = Column('fnum',Integer, primary_key = True)
    attr =  Column('attr',String, primary_key = True)
    
    feed = relationship("Feed")
    
    value = Column('value',String)
    
    __table_args__ = (ForeignKeyConstraint([symname,fnum],[Feed.symname,Feed.fnum], **cc),{})
    def __init__(self,feed,attr,value):
        self.feed = feed
        self.attr = attr
        self.value = value
        
class FeedMunge(Base, ReprMixin):
    __tablename__ = "_feed_munging"
    
    symname = Column('symname',String, primary_key = True)
    fnum = Column('fnum',Integer, primary_key = True)
    order =  Column('order',Integer, primary_key = True)
    mtype = Column('mtype',String)
    method =  Column('method',String)
    
    feed = relationship("Feed")
    
    mungeargs = relationship("FeedMungeArg",lazy="dynamic",cascade="all, delete-orphan")
    
    __table_args__ = (ForeignKeyConstraint([symname,fnum],[Feed.symname,Feed.fnum]),{})
    def __init__(self,order,mtype,method,feed):
        self.order = order
        self.method = method
        self.mtype = mtype
        self.feed = feed
    @property
    def munging_map(self):
        return ProxyDict(self, 'mungeargs', FeedMungeArg, 'arg')
        
class FeedMungeArg(Base, ReprMixin):
    __tablename__ = "_feed_munging_args"
    
    symname = Column('symname',String, primary_key = True)
    fnum = Column('fnum',Integer, primary_key = True)
    order =  Column('order',Integer, primary_key = True)
    arg =  Column('arg',String, primary_key = True)    
    value = Column('value',String)

    feedmunge = relationship("FeedMunge")
    
    __table_args__ = (ForeignKeyConstraint([symname,fnum,order],[FeedMunge.symname,FeedMunge.fnum,FeedMunge.order]),{})
    def __init__(self,arg,value,feedmunge):
        self.arg = arg
        self.value = value
        self.feedmunge = feedmunge
        
class FeedValidity(Base, ReprMixin):
    __tablename__ = "_feed_validity"
    
    symname = Column('symname',String, primary_key = True)
    fnum = Column('fnum',Integer, primary_key = True)
    checkpoint = Column('checkpoint',String, primary_key = True)
    logic = Column('logic',String, primary_key = True)
    key = Column('key',String, primary_key = True)

    feed = relationship("Feed")
    
    value = Column('value',String)

    __table_args__ = (ForeignKeyConstraint([symname,fnum],[Feed.symname,Feed.fnum]),{})
    def __init__(self,feed,checkpoint,logic,key,value=None):
        self.feed = feed
        self.checkpoint = checkpoint
        self.logic = logic
        self.key = key
        self.value = value     

class Override(Base, ReprMixin):
    __tablename__ = '_overrides'

    symname = Column('symname',String, primary_key = True)
    ornum = Column('ornum',Integer,primary_key = True)
    dt_ind = Column('dt_ind',DateTime, nullable=False)

    value = Column('value',Float,nullable=False)
     
    dt_log = Column('dt_log',DateTime,nullable=False)
    user = Column('user',String,nullable=True)
    comment = Column('comment',String,nullable=True)

class FailSafe(Base, ReprMixin):
    __tablename__ = '_failsafes'

    symname = Column('symname',String, primary_key = True)
    fsnum = Column('fsnum',Integer,primary_key = True)
    dt_ind = Column('dt_ind',DateTime, nullable=False)

    value = Column('value',Float,nullable=False)
     
    dt_log = Column('dt_log',DateTime,nullable=False)
    user = Column('user',String,nullable=True)
    comment = Column('comment',String,nullable=True)
    
      

    
try:
    Base.metadata.create_all(engine)
    print "Trump is ready."
except ProgrammingError as e:
    print e.statement
    print e.message
    raise 

if __name__ == '__main__':
    for x in range(3):
        un = str(x) + dt.datetime.now().strftime("%H%M%S")
        
        NewSymbol = Symbol(name="NewSymbol" + un)
        
        NewSymbol.description = 'tester chester 2 ' + un
        NewSymbol.freq = 'D'
        NewSymbol.units = '$'
        
        # Nice to have:
        # NewSymbol.tags = ['Alpha', 'Beta', 'Charlie', 'Delta']
        NewSymbol.addTag("Alpha")
        NewSymbol.addTags(["Beta","Charlie","Delta"])
        
        NewSymbol.addAlias("Newish")
        NewSymbol.addAlias("Newer")
        
        session.commit()
                
        vals = [SymbolValidity(checkpoint='Exception',logic='NoData',key='arg1',value=1,symbol=NewSymbol),
                SymbolValidity(checkpoint='Exception',logic='NoData',key='arg2',value=2,symbol=NewSymbol),
                SymbolValidity(checkpoint='Exception',logic='NoData',key='arg3',value=3,symbol=NewSymbol),
                SymbolValidity(checkpoint='Exception',logic='NoFeed',key='arg1',value=10,symbol=NewSymbol),
                SymbolValidity(checkpoint='Exception',logic='NoFeed',key='arg2',value=20,symbol=NewSymbol)]
    
        session.add_all(vals)
        
        for f in range(4):
            un = str(x) + dt.datetime.now().strftime("%H%M%S")
            NewFeed = Feed(NewSymbol,"DB",
                           sourcing={'stype' : 'DBNonAPICompliant', 'db' : 'General', 'user' : 'TODO'})
                           #TODO:
                           #munging={'mtype' : 'pandas', 'pct_change'})
            
            vals = [FeedValidity(checkpoint='Exception',logic='NoData',key='arg1',value=1,feed=NewFeed),
                    FeedValidity(checkpoint='Exception',logic='NoData',key='arg2',value=2,feed=NewFeed),
                    FeedValidity(checkpoint='Check',logic='NoData',key='arg3',value=3,feed=NewFeed),
                    FeedValidity(checkpoint='Check',logic='NoFeed',key='arg1',value=100,feed=NewFeed),
                    FeedValidity(checkpoint='Check',logic='NoFeed',key='arg2',value='jeff',feed=NewFeed)]
        
            for v in vals:
                session.add(v)
    
            session.add(NewFeed)
        
        NewSymbol.InitializeDataTable()
        
        session.commit()
    session.commit()
    
    
    aSymbol = session.query(Symbol).all()[-1]