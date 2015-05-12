# -*- coding: utf-8 -*-
###############################################################################
#
# PyLint tests that will never be applied by Trump.
#
# ... is not callable, ignored because a property that returns a callable
#                       becomes callable.
# pylint: disable-msg=E1102

# missing parameter, ignored because a SQLAlchemy function is wrapped.
#                    it's a documented issue with that team.
# pylint: disable-msg=E1120

# Used * or ** magic, we're not getting rid of this, it's imperative to Trump.
# pylint: disable-msg=W0142

# Too many/few arguments, ignored, because its confusing and doesn't make
#                         sense to refactor templates.
#
# pylint: disable-msg=R0913
# pylint: disable-msg=R0903

"""
Trump's Object Relational Model is the glue to the framework, used to create
a Symbol's tags, alias, meta data, data feeds and their sources, munging,
error handling and validity instructions.
"""

# SQLAQ - running the uninstall script, then this script, in the same session
#        causes an error:
#
#        sqlalchemy.exc.InvalidRequestError: When initializing mapper
#        Mapper|Feed|_feeds, expression 'FeedMeta' failed to locate a name
#        ("name 'FeedMeta' is not defined"). If this is a class name, consider
#        adding this relationship() to the <class 'trump.orm.Feed'> class
#        after both dependent classes have been defined
#
#        Why?


import datetime as dt

import pandas as pd
from sqlalchemy import event, Table, Column, ForeignKey, ForeignKeyConstraint,\
    String, Integer, Float, Boolean, DateTime, MetaData, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.exc import ProgrammingError, NoSuchTableError
from sqlalchemy.sql import and_
from sqlalchemy import create_engine

from indexing import indexingtypes
from validity import validitychecks
from datadef import datadefs

from trump.tools import ReprMixin, ProxyDict, isinstanceofany, \
    BitFlag, BitFlagType, ReprObjType, DuckTypeMixin

from trump.extensions.symbol_aggs import FeedAggregator, sorted_feed_cols
from trump.templating import bFeed, pab, pnab
from trump.options import read_config, read_settings

from handling import Handler

from reporting.objects import TrumpReport, FeedReport, SymbolReport, \
    ReportPoint

BitFlag.associate_with(BitFlagType)

try:
    ENGINE_STR = read_config(sect='readwrite', sett='engine')
except:
    print ("Problem reading trump.cfg.  Continuing using an in-memory "
           "SQLlite database. Trump was not designed to work in-memory, "
           "because, What's the point of non-persistent persistent objects?")
    ENGINE_STR = "sqlite://"

rbd = read_config(sect='options', sett='raise_by_default')
if rbd.upper() == 'TRUE':
    rbd = BitFlag(1)
else:
    rbd = None

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base = declarative_base()

#metadata = MetaData(bind=engine)

ADO = "all, delete-orphan"
CC = {'onupdate': "CASCADE", 'ondelete': "CASCADE"}

class SymbolManager(object):

    """
    A SymbolManager handles the creation, getting and deletion of symbols.
    It also maintains a global SQLAlchemy session.
    """

    def __init__(self, engine_or_eng_str=None):
        """
        :param ses: session
            Will attempt to use the global SQLAlchemy session, unless
            specified otherwise.
        :return: SymbolManager
        """
        if engine_or_eng_str is None:
            engine = create_engine(ENGINE_STR, echo=False)
        elif isinstance(engine_or_eng_str, (str, unicode)):
            engine = create_engine(engine_or_eng_str, echo=False)
        else:
            engine = engine_or_eng_str
        
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        
        print "Using engine: {}".format(ENGINE_STR)

        self.ses = DBSession()

    def finish(self):
        """
        Closes the session with the database.

        Call after doing any work with Trump.
        """
        self.complete()
        self.ses.close()

    def create(self, name, description=None, units=None,
               agg_method="priority_fill", overwrite=False):
        """
        Create, or get if exists, a Symbol.

        :param name: str
            a symbol's name is a primary key, used across
            the Trump ORM.
        :param description:
            an arbitrary string, used to store user information
            related to the symbol.
        :param units:
            the functionality associated with units, is not
            yet implemented, however, for now, this is simply
            a string used to denote the units of the final
            data Series.
        :param agg_method: str
            the aggregation method, used to calculate
            the final feed.
        :param overwrite: boolean
            set to True, to delete an existing symbol
        :return: Symbol
        """
        """ Create, or gets if exists, a specific Symbol. """
        sym = self.try_to_get(name)

        if sym is not None:
            if overwrite:
                print "Deleting {}".format(sym.name)
                self.ses.delete(sym)
                self.ses.commit()
            else:
                msg = 'Symbol {} already exists.\n' + \
                      'Consider setting overwrite to True.'
                msg = msg.format(name)
                raise Exception(msg)

        sym = Symbol(name, description, units, agg_method)
        
        self.ses.add(sym)

        print "Creating {}".format(sym.name)
        sym.add_alias(name)

        sym.handle = SymbolHandle(sym=sym)
        self.ses.commit()

        return sym

    def delete(self, symbol):
        """
        Deletes a Symbol.
        :param symbol: str or Symbol
        """
        if isinstance(symbol, str):
            sym = self.get(symbol)
        elif isinstance(symbol, Symbol):
            sym = symbol
        else:
            raise Exception("Invalid symbol {}".format((repr(symbol))))
        self.ses.delete(sym)
        self.ses.commit()

    def complete(self):
        """ commits any changes to the database  """
        self.ses.commit()

    def exists(self, symbol):
        """
        checks to see if a symbol exists
        :param symbol: str or Symbol

        :returns: bool
        """

        if isinstance(symbol, str):
            sym = symbol
        elif isinstance(symbol, Symbol):
            sym = symbol.name

        syms = self.ses.query(Symbol).filter(Symbol.name == sym).all()
        if len(syms) == 0:
            return False
        else:
            return True

    def get(self, symbol):
        """
        Gets a Symbol based on name, which is expected to exist. Errors if it
        doesn't exist.

        :param symbol: str

        """
        syms = self.try_to_get(symbol)
        if syms is None:
            raise Exception("Symbol {} does not exist".format(symbol))
        else:
            return syms

    def try_to_get(self, symbol):
        syms = self.ses.query(Symbol).filter(Symbol.name == symbol).all()
        if len(syms) == 0:
            return None
        else:
            return syms[0]

    def search_tag(self, tag):
        """
        Get a list of Symbol objects by searching a tag or partial tag.

        Appending '%' will use SQL's "LIKE" functionality.
        """

        qry = self.ses.query(SymbolTag)

        if "%" in tag:
            syms = qry.filter(SymbolTag.tag.like(tag)).all()
        else:
            syms = qry.filter(SymbolTag.tag == tag).all()
        syms = [tagged.symbol for tagged in syms]
        return syms
    
    def build_view_from_tag(self, tag):
        """
        Build a view of group of Symbols based on their tag.
        
        Appending '%' will use SQL's "LIKE" functionality.
        """
        
        syms = self.search_tag(tag)
        
        names = [sym.name for sym in syms]
        
        subs = ["SELECT indx, '{}' AS symbol, final FROM {}".format(s, s) for s in names]
        
        qry = " UNION ALL ".join(subs)
        
        qry = "CREATE VIEW {} AS {};".format(tag, qry)

        self.ses.execute("DROP VIEW IF EXISTS {};".format(tag))
        self.ses.commit()        
        self.ses.execute(qry)
        self.ses.commit()
    def add_override(self, symbol, ind, val, dt_log=None, user=None, comment=None):
        """
        Appends a single indexed-value pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        Overrides, get applied with highest priority.
        """

        if not isinstance(symbol, (str, unicode)):
            symbol = symbol.name

        if not dt_log:
            dt_log = dt.datetime.now()

        qry = self.ses.query(func.max(Override.ornum).label('max_ornum'))
            
        qry = qry.filter_by(symname = symbol)
        
        cur_ornum = qry.one()
        
        if cur_ornum[0] is None:
            next_ornum = 0
        else:
            next_ornum = cur_ornum[0] + 1            

        tmp = Override(symname=symbol,
                       ind=ind,
                       val=val,
                       dt_log=dt_log,
                       user=user,
                       comment=comment,
                       ornum=next_ornum)
                                             
        self.ses.add(tmp)
        self.ses.commit()

    def add_fail_safe(self, symbol, ind, val,
                      dt_log=None, user=None, comment=None):
        """
        Appends a single indexed-value, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        Fail safes, get applied with the lowest priority.
        """
        if not isinstance(symbol, (str, unicode)):
            symbol = symbol.name

        if not dt_log:
            dt_log = dt.datetime.now()
            
        qry = self.ses.query(func.max(FailSafe.fsnum).label('max_fsnum'))
        qry = qry.filter_by(symname = symbol)
        
        cur_fsnum = qry.one()
        
        if cur_fsnum[0] is None:
            next_fsnum = 0
        else:
            next_fsnum = cur_fsnum[0] + 1        
            
        tmp = FailSafe(symname=symbol,
                       ind=ind,
                       val=val,
                       dt_log=dt_log,
                       user=user,
                       comment=comment,
                       fsnum=next_fsnum)
        self.ses.add(tmp)
        self.ses.commit()

class Symbol(Base, ReprMixin):
    __tablename__ = '_symbols'

    name = Column('name', String, primary_key=True)
    description = Column('description', String)
    units = Column('units', String)
    agg_method = Column('agg_method', String)

    index = relationship('Index', uselist=False, backref='_symbols',
                         cascade=ADO)
    dtype = relationship('SymbolDataDef', uselist=False, backref='_symbols',
                         cascade=ADO)

    handle = relationship("SymbolHandle", uselist=False, backref='_symbols',
                         cascade=ADO)
    tags = relationship("SymbolTag", cascade=ADO)
    aliases = relationship("SymbolAlias", cascade=ADO)
    validity = relationship("SymbolValidity", cascade=ADO)
    feeds = relationship("Feed", cascade=ADO)

    # overrides = relationship("Override",cascade="save-update",
    #              passive_deletes=True)

    def __init__(self, name, description=None, units=None,
                 agg_method="PRIORITY_FILL",
                 indexname="unnamed", indeximp="DatetimeIndexImp"):
        """
        :param name: str
            The name of the symbol to be added to the database, serves
            as a primary key across the trump installation.
        :param description: str, optional
            a description of the symbol, just for notes.
        :param units: str, optional
            a string representing the units for the data.
        :param agg_method: str, default PRIORITY_FILL
            the method used for aggregating feeds, see 
            trump.extensions.symbol_aggs.py for the list of available options.
        :param indexname: str
            a proprietary name assigned to the index.
        :param indeximp: str
            a string representing an index implementer (one of the classes in indexing.py)

        """
        
        self.name = name
        self.description = description
        self.units = units

        self.index = Index(indexname, indeximp, sym=name)
        self.dtype = SymbolDataDef("SkipDataDef", sym=name)
        
        self.agg_method = agg_method
        self.datatable = None
        self.datatable_exists = False
    
    def set_indexing(self, index_template):
        """
        Update a symbol's indexing.  

        :param: index_template, bIndex or bIndex-like
            an index template used to overwrite all 
            details about the symbol's current index.

        :return: None
        
        Changing the indexing implementer works only on indicies of the same
        database type.  Otherwise, the symbol needs to be deleted first.
        """
        objs = object_session(self)
        self.index.name = index_template.name
        self.index.indimp = index_template.imp_name
        self.index.case = index_template.case
        self.index.setkwargs(**index_template.kwargs)
        objs.commit()

    def add_validator(self, val_template):
        """
        Creates and adds a SymbolValidity object to the Symbol.

        :param: validity_template, bValidity or bValidity-like
            a validity template.

        :return: None
        """
        validator = val_template.validator
        
        args = []
        for arg in SymbolValidity.argnames:
            if arg in val_template.__dict__.keys():
                args.append(getattr(val_template, arg))

        objs = object_session(self)
        qry = objs.query(func.max(SymbolValidity.vid).label('max_vid'))
        qry = qry.filter_by(symname = self.name)
        
        cur_vid = qry.one()[0]
        
        if cur_vid is None:
            next_vid = 0
        else:
            next_vid = cur_vid + 1   
            
       
        self.validity.append(SymbolValidity(self, next_vid, validator, *args))
        objs.commit()

    def update_handle(self, chkpnt_settings):
        """
        Update a symbol's handle checkpoint settings

        :param: chkpnt_settings, dict
            a dictionary where the keys are stings representing
            individual handle checkpoint names, for a Symbol
            (eg. caching_of_feeds, feed_aggregation_problem, ...)
            See SymbolHandle.__table__.columns for the
            current list.

            The values can be either integer or BitFlags.

        :return: None
        """

        # Note, for now, this function is nearly identical
        # to the Feed version.  Careful when augmenting,
        # to get the right one.

        objs = object_session(self)

        # override with anything passed in
        for checkpoint in chkpnt_settings:
            if checkpoint in SymbolHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self.handle, checkpoint, settings)
        objs.commit()

    def cache(self, checkvalidity=True):
        """ Re-caches the Symbol's datatable by querying each Feed. """

        data = []
        cols = ['final', 'override_feed000', 'failsafe_feed999']
        
        smrp = SymbolReport(self.name)

        if len(self.feeds) == 0:
            err_msg = "Symbol has no Feeds. Can't cache a feed-less Symbol."
            raise Exception(err_msg)

        smrp
        try:
            datt = datadefs[self.dtype.datadef]
            
            rp = ReportPoint('datadef', 'class', datt)
            smrp.add_reportpoint(rp)
            
            for afeed in self.feeds:
                fdrp = afeed.cache()
                smrp.add_feedreport(fdrp)
                tmp = datt(afeed.data).converted
                data.append(tmp)
                cols.append(afeed.data.name)
        except:
            raise
            point = "caching"
            smrp = self._generic_exception(point, smrp)
                
        try:
            data = pd.concat(data, axis=1)
        except:
            point = "concatenation"
            smrp = self._generic_exception(point, smrp)
       
        indt = indexingtypes[self.index.indimp]
        indkwargs = self.index.getkwargs()
        indt = indt(data, self.index.case, indkwargs)
        data = indt.final_dataframe()

        data_len = len(data)
        data['override_feed000'] = [None] * data_len
        data['failsafe_feed999'] = [None] * data_len
        

        objs = object_session(self)

        qry = objs.query(Override.ind,
                         func.max(Override.dt_log).label('max_dt_log'))
        
        qry = qry.filter_by(symname = self.name)
        
        grb = qry.group_by(Override.ind).subquery()

        qry = objs.query(Override)
        ords = qry.join((grb, and_(Override.ind == grb.c.ind,
                                   Override.dt_log == grb.c.max_dt_log))).all()

        for row in ords:
            data.loc[row.ind, 'override_feed000'] = row.val

        qry = objs.query(FailSafe.ind,
                         func.max(FailSafe.dt_log).label('max_dt_log'))
                         
        qry = qry.filter_by(symname = self.name)
                         
        grb = qry.group_by(FailSafe.ind).subquery()

        qry = objs.query(FailSafe)
        ords = qry.join((grb, and_(FailSafe.ind == grb.c.ind,
                                   FailSafe.dt_log == grb.c.max_dt_log))).all()

        for row in ords:
            data.loc[row.ind, 'failsafe_feed999'] = row.val
            

        try:
            data = data.fillna(value=pd.np.nan)
            data = data[sorted_feed_cols(data)]
            data['final'] = FeedAggregator(self.agg_method).aggregate(data)
        except:
            point = "aggregation"
            smrp = self._generic_exception(point, smrp)


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
        #     self._init_datatable() #older version of _init_datatable
        # delete(self.datatable).execute()
        # self._init_datatable() #older version of _init_datatable

        # Is this the best way to check?
        # if engine.dialect.has_table(session.connection(), self.name):
        #    delete(self.datatable).execute()
        self._refresh_datatable_schema()

        data.index.name = 'indx'
        data = data.reset_index()
        datarecords = data.to_dict(orient='records')
        
        objs = object_session(self)
        objs.execute(self.datatable.insert(), datarecords)
        objs.commit()

        if checkvalidity:
            try:
                isvalid, reports = self.check_validity(report=True)
                for rep in reports:
                    smrp.add_reportpoint(rep)
                if not isvalid:
                    raise Exception('{} is not valid'.format(self.name))
            except:
                point = "validity_check"
                smrp = self._generic_exception(point, smrp)
        
        return smrp

    def check_validity(self, checks=None, report=True):
        
        if report:
            reportpoints = []
            
        allchecks = []
        
        checks_specified=False
        
        if isinstance(checks, (str, unicode)):
            checks = [checks]
            checks_specified = True
        elif isinstance(checks, (list, tuple)):
            checks_specified = True
        else:
            checks = []
            
        for val in self.validity:
            
            if (val.validator in checks) or (not checks_specified):
                ValCheck = validitychecks[val.validator]

                anum = ValCheck.__init__.func_code.co_argcount - 2
                
                args = []
                for arg in SymbolValidity.argnames:
                    args.append(getattr(val, arg))
                
                valid = ValCheck(self.datatable_df, *args[:anum])
                res = valid.result
                allchecks.append(res)
                
                rp = ReportPoint('validation', val.validator, res, str(args[:anum]))
                reportpoints.append(rp)
        
        if report:
            return all(allchecks), reportpoints
        else:
            return all(allchecks)
        
    @property
    def isvalid(self):
        return self.check_validity(report=False)

    @property
    def describe(self):
        """ describes a Symbol, returns a string """
        lines = []
        lines.append("Symbol = {}".format(self.name))
        if len(self.tags):
            tgs = ", ".join(x.tag for x in self.tags)
            lines.append("  tagged = {}".format(tgs))
        if len(self.aliases):
            als = ", ".join(x.alias for x in self.aliases)
            lines.append("  aliased = {}".format(als))
        if len(self.feeds):
            lines.append("  feeds:")

            for fed in self.feeds:
                lines.append("    {}. {}".format(fed.fnum,
                                                       fed.ftype))
        return "\n".join(lines)



    def del_tags(self, tags):
        """ remove a tag or tags from a symbol """
        # SQLA Adding a SymbolTag object, feels awkward/uneccessary.
        # Should I be implementing this functionality a different way?

        if isinstance(tags, (str, unicode)):
            tags = [tags]

        objs = object_session(self)

        docommit = False
        for symboltag in self.tags:
            if symboltag.tag in tags:
                objs.delete(symboltag)
                docommit = True

        if docommit:
            objs.commit()

    def add_tags(self, tags):
        """ add a tag or tags to a symbol """
        # SQLA Adding a SymbolTag object, feels awkward/uneccessary.
        # Should I be implementing this functionality a different way?

        if isinstance(tags, (str, unicode)):
            tags = [tags]

        objs = object_session(self)
        tmps = [SymbolTag(tag=t, sym=self) for t in tags]
        objs.add_all(tmps)
        objs.commit()

    @property
    def n_tags(self):
        """ returns the number of tags  """
        return len(self.tags)

    def add_feed(self, obj, **kwargs):
        if 'fnum' in kwargs:
            fnum = kwargs['fnum']
            del kwargs['fnum']
        else:
            fnum = None

        if isinstance(obj, bFeed):
            munging = obj.munging
            if 'munging' in kwargs:
                explicit_munging = kwargs['munging'].as_odict
                for key in explicit_munging:
                    munging[key] = explicit_munging[key]
            fed = Feed(self, obj.ftype,
                       obj.sourcing,
                       munging,
                       obj.meta,
                       fnum)

        elif isinstance(obj, Feed):
            fed = obj
        else:
            raise Exception("Invalid Feed {}".format(repr(obj)))
        self.feeds.append(fed)
        
        objs = object_session(self)
        objs.add(fed)

        # SQLAQ - With Postgres, I don't need this commit here.
        # with SQLite, I do. On SQLite, if I don't have it, I get a really
        # strange situation where self.feeds can have two identical Feeds
        # matching, after only ever calling add_feed ONCE, on a brand new
        # SQLite file.
        objs.commit()

    def add_alias(self, obj):
        
        objs = object_session(self)
        
        if isinstance(obj, list):
            raise NotImplementedError
        elif isinstanceofany(obj, (str, unicode)):
            a = SymbolAlias(self, obj)
            self.aliases.append(a)
            objs.add(a)

    def data(self):
        """
        :return: rows from the datatable
        """
        dtbl = self.datatable

        objs = object_session(self)
        if isinstance(dtbl, Table):
            return objs.query(dtbl.c.indx, dtbl.c.final).all()
        else:
            raise Exception("Symbol has no datatable")

    def alldata(self):
        """
        :return: all data from the datatable
        """
        dtbl = self.datatable
        cols = (getattr(dtbl.c, col) for col in self.dt_all_cols)
        
        objs = object_session(self)
        if isinstance(dtbl, Table):
            return objs.query(*cols).all()
        else:
            raise Exception("Symbol has no datatable")

    @property
    def df(self):
        """ returns the dataframe representation of the symbol's final data """
        data = self.data()
        adf = pd.DataFrame(data)
        adf.columns = [self.index.name, self.name]
        
        datt = datadefs[self.dtype.datadef]       
        adf[self.name] = datt(adf[self.name]).converted
        
        adf = adf.set_index(self.index.name)

        indt = indexingtypes[self.index.indimp]
        indt = indt(adf, self.index.case, self.index.getkwargs())
        adf = indt.final_series()

        return adf

    @property
    def datatable_df(self):
        """ returns the dataframe representation of the symbol's final data """
        data = self.alldata()
        adf = pd.DataFrame(data)
        
        adf.columns = self.dt_all_cols
        
        datt = datadefs[self.dtype.datadef]
        
        for col in adf.columns:
            adf[col] = datt(adf[col]).converted
        
        adf = adf.set_index('indx')

        indt = indexingtypes[self.index.indimp]
        indt = indt(adf, self.index.case, self.index.getkwargs())
        adf = indt.raw_data()

        return adf
        
    def del_feed(self):
        """ remove a feed """
        raise NotImplementedError

    def add_feeds(self, symbol, ftype, sourcing, munging=None, fnum=None):
        """ add several feeds with one method """
        raise NotImplementedError

    @property
    def n_feeds(self):
        """ returns the number of feeds """
        return len(self.feeds)

    def set_description(self, description):
        """ change the description of the symbol """
        self.description = description

    def set_units(self, units):
        """ change the symbol's units """
        self.units = units

    def _init_datatable(self):
        """
        Instantiates the .datatable attribute, pointing to a table in the
        database that stores all the cached data
        """
        try:
            self.datatable = Table(self.name, Base.metadata, autoload=True)
        except NoSuchTableError:
            print "Creating datatable, cause it doesn't exist"
            self.datatable = self._datatable_factory()
            self.datatable.create()
        self.datatable_exists = True

    def _refresh_datatable_schema(self):
        objs = object_session(self)
        self.datatable = self._datatable_factory()
        self.datatable.drop(checkfirst=True)
        self.datatable.create()
        self.datatable_exists = True
        objs.commit()

    def _datatable_factory(self):
        """
        creates a SQLAlchemy Table object with the appropriate number of
        columns given the number of feeds
        """
        feed_cols = ['feed{0:03d}'.format(i + 1) for i in range(self.n_feeds)]
        feed_cols = ['override_feed000'] + feed_cols + ['failsafe_feed999']

        ind_sqlatyp = indexingtypes[self.index.indimp].sqlatyp
        dat_sqlatyp = datadefs[self.dtype.datadef].sqlatyp

        atbl = Table(self.name, Base.metadata,
                     Column('indx', ind_sqlatyp, primary_key=True),
                     Column('final', dat_sqlatyp),
                     *(Column(fed_col, dat_sqlatyp) for fed_col in feed_cols),
                     extend_existing=True)
        
        self.dt_feed_cols = feed_cols[:]
        self.dt_all_cols = ['indx', 'final'] + feed_cols[:]
        return atbl
    def _generic_exception(self, point, reporter):
        logic = getattr(self.handle, point)
        msg = "Exception at the point of {} for {}"
        msg = msg.format(point, self.name)
        hdlrp = Handler(logic, point, msg).process()
        if hdlrp:
            reporter.add_handlepoint(hdlrp)
        return reporter

@event.listens_for(Symbol, 'load')
def __receive_load(target, context):
    """ loads a symbols datatable upon being queried """
    target._init_datatable()


def set_symbol_or_symname(self, sym):
    if isinstance(sym, (str, unicode)):
        setattr(self, "symname", sym)
    else:
        setattr(self, "symbol", sym)


class SymbolTag(Base, ReprMixin):
    __tablename__ = '_symbol_tags'
    symname = Column('symname', String, ForeignKey('_symbols.name', **CC),
                     primary_key=True)
    tag = Column('tag', String, primary_key=True)

    symbol = relationship("Symbol")

    def __init__(self, tag, sym=None):
        set_symbol_or_symname(self, sym)
        self.tag = tag

class SymbolDataDef(Base, ReprMixin):
    __tablename__ = "_symbol_datadef"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    datadef = Column("datadef", String, nullable=False)
    """string representing a :py:class:`~trump.datadef.DataDefiner`."""
    
    def __init__(self, datadef, sym=None):

        set_symbol_or_symname(self, sym)
        self.datadef = datadef
        
class SymbolAlias(Base, ReprMixin):
    __tablename__ = '_symbol_aliases'
    symname = Column('symname', String, ForeignKey('_symbols.name', **CC),
                     primary_key=True)
    alias = Column('alias', String, primary_key=True)

    symbol = relationship("Symbol")

    def __init__(self, symbol, alias):
        self.symbol = symbol
        self.alias = alias


class SymbolValidity(Base, ReprMixin):
    __tablename__ = "_symbol_validity"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    vid = Column('vid', Integer, primary_key=True, nullable=False)

    validator = Column('validator', String, nullable=False)
    
    argnames = ['arg' + a for a in list('abcde')]
    
    arga = Column('arga', ReprObjType)
    argb = Column('argb', ReprObjType)
    argc = Column('argc', ReprObjType)
    argd = Column('argd', ReprObjType)
    arge = Column('arge', ReprObjType)
        
    symbol = relationship("Symbol")

    def __init__(self, symbol, vid, validator, *args):
        set_symbol_or_symname(self, symbol)

        self.vid = vid

        self.validator = validator
        
        pads = [None] * (len(self.argnames) - len(args))
        argvals = list(args) + pads
        for i, arg in enumerate(self.argnames):
            setattr(self, arg, argvals[i])
            


class SymbolHandle(Base, ReprMixin):
    """
    Stores instructions about specific handle points during
    Symbol caching:

    .. code-block:: python

        sh = SymbolHandle({'aggregation' : BitFlag(36)}, aSymbol)
        >>> sh.aggregation['email']
        True

    """
    __tablename__ = "_symbol_handle"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    caching = Column('caching', BitFlagType)
    concatenation = Column('concatenation', BitFlagType)
    aggregation = Column('aggregation', BitFlagType)
    validity_check = Column('validity_check', BitFlagType)

    symbol = relationship("Symbol")

    def __init__(self, chkpnt_settings={}, sym=None):
        """
        :param chkpnt_settings: dict
            A dictionary with keys matching names of the handle points
            and the values either integers or BitFlags
        :param str or sym: Symbol
            The Symbol that this SymbolHandle is associated with it.
        """
        set_symbol_or_symname(self, sym)

        self.caching = rbd or BitFlag(0)
        self.concatenation = rbd or BitFlag(['raise'])
        self.aggregation = rbd or BitFlag(['stdout'])
        self.validity_check = rbd or BitFlag(['report'])

        # override with anything passed in settings
        for checkpoint in chkpnt_settings:
            if checkpoint in SymbolHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self, checkpoint, settings)

class Index(Base, ReprMixin):
    __tablename__ = "_indicies"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    name = Column("name", String, nullable=False)
    """string to name the index, only used when serving."""

    indimp = Column("indimp", String, nullable=False)
    """string representing a :py:class:`~trump.indexing.IndexImplementer`."""

    case = Column("case", String)
    """string used in a :class:`~.indexing.IndexImplementer` switch statement."""

    kwargs = relationship("IndexKwarg", lazy="dynamic", cascade=ADO)

    def __init__(self, name, indimp, case=None, kwargs={}, sym=None):

        set_symbol_or_symname(self, sym)

        self.name = name
        self.indimp = indimp
        self.case = case or "asis"
        self.setkwargs(**kwargs)

    def setkwargs(self, **kwargs):
        self.kwargs = []
        if kwargs is not None:
            list_of_kwargs = []
            for kword, val in kwargs.iteritems():
                list_of_kwargs.append(IndexKwarg(kword, val))
            self.kwargs = list_of_kwargs
        else:
            self.kwargs = []

    def getkwargs(self):
        kwargs = {}
        for indkw in self.kwargs:
            kwargs[indkw.kword] = indkw.val
        return kwargs


class IndexKwarg(Base, ReprMixin, DuckTypeMixin):
    __tablename__ = "_index_kwargs"

    symname = Column('symname', String, ForeignKey('_indicies.symname', **CC),
                     primary_key=True)

    kword = Column('kword', String, primary_key=True)

    _colswitch = Column('colswitch', Integer)

    boolcol = Column('boolcol', Boolean)
    strcol = Column('strcol', String)
    intcol = Column('intcol', Integer)
    floatcol = Column('floatcol', Float)
    reprcol = Column('reprcol', ReprObjType)

    def __init__(self, kword, val):
        self.kword = kword
        self.setval(val)

class Feed(Base, ReprMixin):

    """
    The Feed object stores parameters associated with souring and munging
    a single series.
    """
    __tablename__ = "_feeds"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)

    state = Column('state', String, nullable=False)
    ftype = Column('ftype', String, nullable=False)

    handle = relationship("FeedHandle", uselist=False, backref='_feeds',
                          cascade=ADO)

    tags = relationship("FeedTag", cascade=ADO)
    sourcing = relationship("FeedSource", lazy="dynamic", cascade=ADO)
    meta = relationship("FeedMeta", lazy="dynamic", cascade=ADO)
    munging = relationship("FeedMunge", lazy="dynamic", cascade=ADO)

    symbol = relationship("Symbol")
        
    def __init__(self, symbol, ftype, sourcing,
                 munging=None, meta=None, fnum=None):
        self.ftype = ftype
        self.state = "ON"
        self.symbol = symbol
        self.data = None

        self.ses = object_session(symbol)

        if fnum is None:
            qry = self.ses.query(Feed.fnum)
            existing_fnums = qry.filter(Feed.symname == symbol.name).all()
            existing_fnums = [n[0] for n in existing_fnums]
            if len(existing_fnums) == 0:
                self.fnum = 0
            else:
                self.fnum = max(existing_fnums) + 1
        else:
            self.fnum = fnum

        if meta:
            for key in meta:
                tmp = FeedMeta(attr=key, value=meta[key], feed=self)
                self.ses.add(tmp)
                self.meta_map[key] = tmp
                self.ses.commit()

        if sourcing:
            sk = None
            if 'sourcing_key' in meta:
                sk = meta['sourcing_key']
            fsrc = FeedSource(meta['stype'], sk, self)
            for key in sourcing:
                if key not in ('stype', 'sourcing_key'):
                    fsrckw = FeedSourceKwarg(key, sourcing[key], fsrc)
                    fsrc.sourcekwargs.append(fsrckw)
            self.sourcing.append(fsrc)
        
        self.ses.commit()

        if munging:
            for i, meth in enumerate(munging.keys()):
                fmg = FeedMunge(order=i, mtype=munging[meth]['mtype'],
                                method=meth, feed=self)
                for arg, value in munging[meth]['kwargs'].iteritems():
                    if not isinstance(value, (int, float)):
                        val = str(value)
                    else:
                        val = value
                    fmg.mungeargs.append(FeedMungeKwarg(arg, val, feedmunge=fmg))
                self.munging.append(fmg)
        
        self.ses.commit()

        self.handle = FeedHandle(feed=self)
        
        self.ses.commit()

    def update_handle(self, chkpnt_settings):
        """
        Update a feeds's handle checkpoint settings

        :param chkpnt_settings, dict:
            a dictionary where the keys are stings representing
            individual handle checkpoint names, for a Feed
            (eg. api_failure, empty_feed, index_type_problem...)
            See FeedHandle.__table__.columns for the
            current list.

            The values can be either integer or BitFlags.

        :return: None
        """

        # Note, for now, this function is nearly identical
        # to the Symbol version.  Careful when augmenting,
        # to get the right one.

        objs = object_session(self)

        # override with anything passed in
        for checkpoint in chkpnt_settings:
            if checkpoint in FeedHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self.handle, checkpoint, settings)
        objs.commit()

    def cache(self):
        
        fdrp = FeedReport(self.fnum)

        src = self.sourcing.one()
        srckeys = src.sourcing_map.keys()
        kwargs = {k: src.sourcing_map[k].val for k in srckeys}
               
        sourcing_key = src.sourcing_key
        stype = src.stype

        # If there is a sourcing key defined, use it to override any database
        # defined parameters
        if sourcing_key:
            sourcing_overrides = read_settings()[stype][sourcing_key]
            for key in sourcing_overrides:
                kwargs[key] = sourcing_overrides[key]

        rp = ReportPoint('readmeta', 'sourcing', stype, str(kwargs))
        fdrp.add_reportpoint(rp)
        
        try:
            # Depending on the feed type, use the kwargs appropriately to
            # populate a dataframe, self.data.

            # For development of the handler, raise an exception...
            # raise Exception("There was a problem of somekind!")

            if stype == 'Quandl':
                import Quandl as q
                self.data = q.get(**kwargs)
                try:
                    fn = kwargs['fieldname']
                except KeyError:
                    raise KeyError("fieldname wasn't specified in Quandl Feed")

                try:
                    self.data = self.data[fn]
                except KeyError:
                    kemsg = """{} was not found in list of Quandle headers:\n
                             {}""".format(fn, str(self.data.columns))
                    raise KeyError(kemsg)

            elif stype == 'psycopg2':
                dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
                import psycopg2 as db
                con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}
                con = db.connect(**con_kwargs)
                raise NotImplementedError("pyscopg2")
            elif stype == 'DBAPI':
                dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
                db = __import__(self.ses.bind.driver)
                con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}

                con = db.connect(**con_kwargs)
                cur = con.cursor()

                if 'command' in kwargs:
                    cur.execute(kwargs['command'])
                elif set(['table', 'indexcol', 'datacol']).issubset(kwargs.keys()):

                    rel = (kwargs[c] for c in ['indexcol', 'datacol', 'table'])
                    qry = "SELECT {0},{1} FROM {2} ORDER BY {0};".format(*rel)
                    cur.execute(qry)

                results = [(row[0], row[1]) for row in cur.fetchall()]
                con.close()
                ind, dat = zip(*results)
                self.data = pd.Series(dat, ind)
            elif stype == 'SQLAlchemy':
                NotImplementedError("SQLAlchemy")
            elif stype == 'PyDataCSV':
                from pandas import read_csv

                col = kwargs['data_column']
                del kwargs['data_column']
                
                fpob = kwargs['filepath_or_buffer']
                del kwargs['filepath_or_buffer']
                
                df = read_csv(fpob, **kwargs)
                
                self.data = df[col]

            elif stype == 'PyDataDataReaderST':
                import pandas.io.data as pydata

                fmt = "%Y-%m-%d"
                if 'start' in kwargs:
                    kwargs['start'] = dt.datetime.strptime(kwargs['start'], fmt)
                if 'end' in kwargs:
                    if kwargs['end'] == 'now':
                        kwargs['end'] = dt.datetime.now()
                    else:
                        kwargs['end'] = dt.datetime.strptime(kwargs['end'], fmt)

                col = kwargs['data_column']
                del kwargs['data_column']

                adf = pydata.DataReader(**kwargs)
                self.data = adf[col]

            else:
                raise Exception("Unknown Source Type : {}".format(stype))
        except:
            point = "api_failure"
            fdrp = self._generic_exception(point, fdrp)
            self.data = pd.Series()

        try:
            if len(self.data) == 0 or self.data.empty:
                raise Exception('Feed is empty')
        except:
            point = "empty_feed"
            fdrp = self._generic_exception(point, fdrp)

        try:
            if not (self.data.index.is_monotonic and self.data.index.is_unique):
                raise Exception('Feed index is not uniquely monotonic')
        except:
            point = "monounique"
            fdrp = self._generic_exception(point, fdrp)

        # munge accordingly
        print "Munging..."
        
        print self.data.tail(5)
        
        for mgn in self.munging:
            #print mgn
            #print mgn.munging_map.keys()
            mmkeys = mgn.munging_map.keys()
            kwargs = {k: mgn.munging_map[k].val for k in mmkeys}
            if mgn.mtype == pab:
                afunc = getattr(self.data, mgn.method)
                self.data = afunc(**kwargs)
            elif mgn.mtype == pnab:
                lib = __import__('pandas', globals(), locals(), [], -1)
                afunc = getattr(lib, mgn.method)
                self.data = afunc(self.data, **kwargs)

        # make sure it's named properly...
        self.data.name = "feed" + str(self.fnum + 1).zfill(3)

        rp = ReportPoint('finish', 'cache', True, self.data.tail(3))
        fdrp.add_reportpoint(rp)
        
        return fdrp

#            for a in mgn.methodargs:
#                args[a.arg] = a.value
#            self.data = munging_methods[mgn.method](self.data,**args)

    @property
    def meta_map(self):
        return ProxyDict(self, 'meta', FeedMeta, 'attr')

    @property
    def source(self):
        return " ".join([p.key + " : " + p.value for p in self.sourcing])
    def _generic_exception(self, point, reporter):
        logic = getattr(self.handle, point)
        msg = "Exceptoin for feed #{} for {} at the {} point."
        msg = msg.format(self.fnum, self.symname, point)
        msg = msg.format(point, self.name)
        hdlrp = Handler(logic, point, msg).process()
        if hdlrp:
            reporter.add_handlepoint(hdlrp)
        return reporter

class FeedTag(Base, ReprMixin):
    __tablename__ = '_feed_tags'
    symname = Column('symname', String, primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)

    tag = Column('tag', String, primary_key=True)

    feed = relationship("Feed")

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum],
                                **CC)
    __table_args__ = (fkey, {})
        
class FeedSource(Base, ReprMixin):
    __tablename__ = "_feed_sourcing"

    symname = Column('symname', String, primary_key=True)
    
    fnum = Column('fnum', Integer, primary_key=True)

    stype = Column('stype', String)
    sourcing_key = Column('sourcing_key', String)
    
    feed = relationship("Feed")
    sourcekwargs = relationship("FeedSourceKwarg", lazy="dynamic", cascade=ADO)

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum],
                                **CC)

    __table_args__ = (fkey, {})

    def __init__(self, stype, sourcing_key, feed):
        self.stype = stype
        self.sourcing_key = sourcing_key
        self.feed = feed
    @property
    def sourcing_map(self):
        return ProxyDict(self, 'sourcekwargs', FeedSourceKwarg, 'kword')

class FeedSourceKwarg(Base, ReprMixin, DuckTypeMixin):
    __tablename__ = "_feed_sourcing_kwargs"

    symname = Column('symname', String, primary_key=True)
                     
    fnum = Column('fnum', Integer, primary_key=True)

    kword = Column('kword', String, primary_key=True)
    
    _colswitch = Column('colswitch', Integer)

    boolcol = Column('boolcol', Boolean)
    strcol = Column('strcol', String)
    intcol = Column('intcol', Integer)
    floatcol = Column('floatcol', Float)
    reprcol = Column('reprcol', ReprObjType)
    
    feedsource = relationship("FeedSource")

    fkey = ForeignKeyConstraint([symname, fnum],
                                [FeedSource.symname,
                                 FeedSource.fnum])
    __table_args__ = (fkey, {})

    def __init__(self, kword, val, feedsource):
        self.kword = kword
        self.setval(val)
        self.feedsource = feedsource

class FeedMeta(Base, ReprMixin):
    __tablename__ = "_feed_meta"

    symname = Column('symname', String, primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)
    attr = Column('attr', String, primary_key=True)

    feed = relationship("Feed")

    value = Column('value', String)

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum],
                                **CC)
    __table_args__ = (fkey, {})

    def __init__(self, feed, attr, value):
        self.feed = feed
        self.attr = attr
        self.value = value


class FeedMunge(Base, ReprMixin):
    __tablename__ = "_feed_munging"

    symname = Column('symname', String, primary_key=True)
    
    fnum = Column('fnum', Integer, primary_key=True)
    order = Column('order', Integer, primary_key=True)
    mtype = Column('mtype', String)
    method = Column('method', String)

    feed = relationship("Feed")
    mungeargs = relationship("FeedMungeKwarg", lazy="dynamic", cascade=ADO)

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum])
    __table_args__ = (fkey, {})

    def __init__(self, order, mtype, method, feed):
        self.order = order
        self.method = method
        self.mtype = mtype
        self.feed = feed

    @property
    def munging_map(self):
        return ProxyDict(self, 'mungeargs', FeedMungeKwarg, 'kword')


class FeedMungeKwarg(Base, ReprMixin, DuckTypeMixin):
    __tablename__ = "_feed_munging_kwargs"

    symname = Column('symname', String, primary_key=True)
                     
    fnum = Column('fnum', Integer, primary_key=True)
    order = Column('order', Integer, primary_key=True)

    kword = Column('kword', String, primary_key=True)
    
    _colswitch = Column('colswitch', Integer)

    boolcol = Column('boolcol', Boolean)
    strcol = Column('strcol', String)
    intcol = Column('intcol', Integer)
    floatcol = Column('floatcol', Float)
    reprcol = Column('reprcol', ReprObjType)
    
    feedmunge = relationship("FeedMunge")

    fkey = ForeignKeyConstraint([symname, fnum, order],
                                [FeedMunge.symname,
                                 FeedMunge.fnum,
                                 FeedMunge.order])
    __table_args__ = (fkey, {})

    def __init__(self, kword, val, feedmunge):
        self.kword = kword
        self.setval(val)
        self.feedmunge = feedmunge


class FeedHandle(Base, ReprMixin):
    """
    Stores instructions about specific handle points during
    Feed caching:

    .. code-block:: python

        fh = FeedHandle({'api_failure' : BitFlag(36)}, aSymbol.feeds[0])
        >>> fh.api_failure['email']
        True

    """
    __tablename__ = "_feed_handle"

    symname = Column('symname', String, primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)

    api_failure = Column('api_failure', BitFlagType)
    empty_feed = Column('empty_feed', BitFlagType)
    index_type_problem = Column('index_type_problem', BitFlagType)
    index_property_problem = Column('index_property_problem', BitFlagType)
    data_type_problem = Column('data_type_problem', BitFlagType)
    monounique = Column('monounique', BitFlagType)

    feed = relationship("Feed")

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum])
    __table_args__ = (fkey, {})

    def __init__(self, chkpnt_settings={}, feed=None):
        """
        :param chkpnt_settings: dict
            A dictionary with keys matchin names of the handle points
            and the values either integers or BitFlags
        :param feed: Feed
            The feed that this FeedHandle is associated with it.
        """
        self.feed = feed

        self.api_failure = rbd or BitFlag(['raise'])
        self.empty_feed = rbd or BitFlag(['stdout', 'report'])
        self.index_type_problem = rbd or BitFlag(['stdout', 'report'])
        self.index_property_problem = rbd or BitFlag(['stdout'])
        self.data_type_problem = rbd or BitFlag(['stdout', 'report'])
        self.monounique = rbd or BitFlag(['raise'])

        # override with anything passed in settings
        for checkpoint in chkpnt_settings:
            if checkpoint in FeedHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self, checkpoint, settings)


class Override(Base, ReprMixin):
    """
    An Override represents a single datapoint with an associated
    index value, applied to a Symbol's datatable after sourcing all the
    data, and will be applied after any aggregation logic
    """
    __tablename__ = '_overrides'

    symname = Column('symname', String, primary_key=True)
    """ symbol name, for the override"""

    ornum = Column('ornum', Integer, primary_key=True)
    """ Override number, uniquely assigned to every override"""

    ind = Column('ind', ReprObjType, nullable=False)
    """ the repr of the object used in the Symbol's index."""

    val = Column('val', ReprObjType, nullable=False)
    """ the repr of the object used as the Symbol's value."""

    dt_log = Column('dt_log', DateTime, nullable=False)
    """ datetime that the override was created"""

    user = Column('user', String, nullable=True)
    """ user name or process name that created the override"""

    comment = Column('comment', String, nullable=True)
    """ a user field to store an arbitrary string about the override"""

    # make a constructor just so sphinx doesn't pick up the
    # base's __init__'s doc string.

    def __init__(self, *args, **kwargs):
        super(Override, self).__init__(*args, **kwargs)


class FailSafe(Base, ReprMixin):
    """
    A FailSafe represents a single datapoint with an associated
    index value, applied to a Symbol's datatable after sourcing all the
    data, and will be applied after any aggregation logic, only
    where no other datapoint exists. It's a back-up datapoint,
    used only by Trump, when an NA exists.

    .. note::

       only datetime based indices with float-based data currently work with
       Overrides

    """

    __tablename__ = '_failsafes'

    symname = Column('symname', String, primary_key=True)
    """ symbol name, for the override"""

    fsnum = Column('fsnum', Integer, primary_key=True)
    """ Failsafe number, uniquely assigned to every FailSafe"""

    ind = Column('ind', ReprObjType, nullable=False)
    """ the repr of the object used in the Symbol's index."""

    val = Column('val', ReprObjType, nullable=False)
    """ the repr of the object used as the Symbol's value."""

    dt_log = Column('dt_log', DateTime, nullable=False)
    """ datetime of the FailSafe creation."""

    user = Column('user', String, nullable=True)
    """ user name or process name that created the FailSafe"""

    comment = Column('comment', String, nullable=True)
    """ user field to store an arbitrary string about the FailSafe"""

    # make a constructor just so sphinx doesn't pick up the
    # base's __init__'s doc string.

    def __init__(self, *args, **kwargs):
        super(FailSafe, self).__init__(*args, **kwargs)

def SetupTrump(engine_string=None):
    
    engine_str = engine_string or ENGINE_STR
    
    try:
        engine = create_engine(engine_str)
        #Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        print "Trump is installed @ " + engine_str
        return engine
    except ProgrammingError as pgerr:
        print pgerr.statement
        print pgerr.message
        raise
    return True

if __name__ == '__main__':

    ind = Index("newind", "date_range")

    session.add(ind)

    kw = {'start': '201001', 'end': '201002', 'freq': None}
    ind.setkwargs(**kw)

    session.commit()

    print ind.getkwargs()
