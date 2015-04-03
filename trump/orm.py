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
    String, Integer, Float, DateTime, MetaData, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlalchemy.sql import and_
from sqlalchemy import create_engine

from trump.tools import ReprMixin, ProxyDict, BitFlag, BitFlagType, \
    isinstanceofany
from trump.extensions.symbol_aggs import apply_row, choose_col
from trump.templating import bFeed, pab, pnab
from trump.options import read_config, read_settings

BitFlag.associate_with(BitFlagType)

ENGINE_STR = read_config('readwrite')['engine']
engine = create_engine(ENGINE_STR, echo=False)
print ENGINE_STR
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

metadata = MetaData(bind=engine)

ADO = "all, delete-orphan"
CC = {'onupdate': "CASCADE", 'ondelete': "CASCADE"}

CHECKPOINTS = ('EXCEPTION', 'CHECK')
# STATE = ('ENABLED', 'DISABLED', 'ERROR')


class SymbolManager(object):
    """
    A SymbolManager handles the creation, getting and deletion of symbols.
    """
    def __init__(self, ses=None):
        self.ses = ses or session

    def finish(self):
        """
        Closes the session with the database.

        Call after doing any work with Trump.
        """
        self.ses.close()

    def create(self, name, description=None, freq=None, units=None,
               agg_method="PRIORITY_FILL"):
        """ Create, or gets if exists, a Symbol. """
        sym = self.try_to_get(name)
        if sym is not None:
            print "Deleting {}".format(sym.name)
            self.ses.delete(sym)
            self.ses.commit()

        sym = Symbol(name, description, freq, units, agg_method)

        print "Creating {}".format(sym.name)
        sym.add_alias(name)

        sym.handle = SymbolHandle(sym=sym)
        self.ses.commit()

        return sym

    def delete(self, symbol):
        """ Deletes a Symbol. """
        if isinstance(symbol, str):
            sym = self.get(symbol)
        elif isinstance(symbol, Symbol):
            sym = symbol
        else:
            raise Exception("Invalid symbol {}".format((repr(symbol))))
        del sym
        self.ses.commit()

    def complete(self):
        """ commits any changes to the session  """
        self.ses.commit()

    def exists(self, symbol):
        """
        checks to see if a symbol exists

        returns boolean
        """
        syms = self.ses.query(Symbol).filter(Symbol.name == symbol).all()
        if len(syms) == 0:
            return False
        else:
            return True

    def get(self, symbol):
        """
        Gets a Symbol based on name, which is expected to exist. Errors if it
        doesn't exist.
        """
        syms = self.try_to_get(symbol)
        if syms == None:
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


class Symbol(Base, ReprMixin):
    """
    agg_method : see extensions.symbol_aggs.py and look at the wrapped function
    names.
    """
    __tablename__ = '_symbols'

    name = Column('name', String, primary_key=True)
    description = Column('description', String)
    freq = Column('freq', String)
    units = Column('units', String)
    agg_method = Column('agg_method', String)

    handle = relationship("SymbolHandle", uselist=False, backref='_symbols', cascade=ADO)

    tags = relationship("SymbolTag", cascade=ADO)
    aliases = relationship("SymbolAlias", cascade=ADO)
    validity = relationship("SymbolValidity", cascade=ADO)
    feeds = relationship("Feed", cascade=ADO)

    # overrides = relationship("Override",cascade="save-update",
    #              passive_deletes=True)

    def __init__(self, name, description=None, freq=None, units=None,
                 agg_method="PRIORITY_FILL"):
        """
        Parameters
        ----------
        name : str
            The name of the symbol to be added to the database, serves
            as a primary key across the trump installation.
        description : str, optional
            a description of the symbol, just for notes.
        freq : str, optional
            a pandas dateoffset string.
        units : str, optional
            a string representing the units for the data.
        agg_method : str, default PRIORITY_FILL
            the method used for aggregating feeds, see 
            trump.extensions.symbol_aggs.py for the list of available options.
            
        """
        self.name = name
        self.description = description
        self.freq = freq
        self.units = units
        self.agg_method = agg_method
        self.datatable = None
        self.datatable_exists = False
        # SQLAQ - Is this okay to do? It feels sneaky, dirty and wrong.
        session.add(self)

    def update_handle(self, chkpnt_settings):
        """
        Update a symbol's handle checkpoint settings

        :param chkpnt_settings, dict:
            a dictionary where the keys are stings representing
            individual handle checkpoint names, for a Symbol
            (eg. caching_of_feeds, feed_aggregation_problem, ...)
            See SymbolHandle.__table__.columns for the
            current list.

            The values can be either integer or BitFlags.

        :return: None
        """

        objs = object_session(self)

        # override with anything passed in
        for checkpoint in chkpnt_settings:
            if checkpoint in SymbolHandle.__table__.columns:
                print "updating handle..."
                settings = chkpnt_settings[checkpoint]
                print settings
                setattr(self.handle, checkpoint, settings)
        objs.commit()

    def cache_feed(self, fid):
        raise NotImplementedError

    def cache(self):
        """ Re-caches the Symbol's datatable by quering each Feed. """

        data = []
        cols = ['final', 'override_feed000', 'failsafe_feed999']

        if len(self.feeds) == 0:
            err_msg = "Symbol has no Feeds. Can't cache a feed-less Symbol."
            raise Exception(err_msg)

        for afeed in self.feeds:
            afeed.cache()
            data.append(afeed.data)
            cols.append(afeed.data.name)

        data = pd.concat(data, axis=1)

        data_len = len(data)
        data['override_feed000'] = [None] * data_len
        data['failsafe_feed999'] = [None] * data_len

        objs = object_session(self)

        qry = objs.query(Override.dt_ind,
                         func.max(Override.dt_log).label('max_dt_log'))
        grb = qry.group_by(Override.dt_ind).subquery()

        qry = objs.query(Override)
        ords = qry.join((grb, and_(Override.dt_ind == grb.c.dt_ind,
                                   Override.dt_log == grb.c.max_dt_log))).all()

        for row in ords:
            data.loc[row.dt_ind, 'override_feed000'] = row.value

        qry = objs.query(FailSafe.dt_ind,
                         func.max(FailSafe.dt_log).label('max_dt_log'))
        grb = qry.group_by(FailSafe.dt_ind).subquery()

        qry = objs.query(FailSafe)
        ords = qry.join((grb, and_(FailSafe.dt_ind == grb.c.dt_ind,
                                   FailSafe.dt_log == grb.c.max_dt_log))).all()

        for row in ords:
            data.loc[row.dt_ind, 'failsafe_feed999'] = row.value

        if self.agg_method in apply_row:
            data['final'] = data.apply(apply_row[self.agg_method], axis=1)
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
        #     self._init_datatable()
        # delete(self.datatable).execute()
        # self._init_datatable()

        # Is this the best way to check?
        # if engine.dialect.has_table(session.connection(), self.name):
        #    delete(self.datatable).execute()
        self._init_datatable()

        data.index.name = 'datetime'
        data = data.reset_index()
        session.execute(self.datatable.insert(),
                        data.to_dict(orient='records'))

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
                lines.append("    {}. {} -> {}".format(fed.fnum,
                                                       fed.ftype,
                                                       fed.source_str()))
                printed_cp = []
        return "\n".join(lines)

    def add_override(self, dt_ind, value, dt_log=None, user=None, comment=None):
        """
        appends a single value and date pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable

        Overrides, get applied with highest priority.
        """
        objs = object_session(self)

        if not dt_log:
            dt_log = dt.datetime.now()

        tmp = Override(symname=self.name,
                       dt_ind=dt_ind,
                       value=value,
                       dt_log=dt_log,
                       user=user,
                       comment=comment)
        objs.add(tmp)
        objs.commit()

    def add_fail_safe(self, dt_ind, value,
                      dt_log=None, user=None, comment=None):
        """
        appends a single value and date pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        Failsafes, get applied with highest priority.
        """
        objs = object_session(self)

        if not dt_log:
            dt_log = dt.datetime.now()

        tmp = FailSafe(symname=self.name,
                       dt_ind=dt_ind,
                       value=value,
                       dt_log=dt_log,
                       user=user,
                       comment=comment)
        objs.add(tmp)
        objs.commit()

    def del_tags(self,tags):
        """ remove a tag or tags from a symbol """
        # SQLA Adding a SymbolTag object, feels awkward/uneccessary.
        # Should I be implementing this functionality a different way?

        if isinstance(tags,(str,unicode)):
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

        if isinstance(tags,(str,unicode)):
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
                       obj.validity,
                       obj.meta,
                       fnum)
        elif isinstance(obj, Feed):
            fed = obj
        else:
            raise Exception("Invalid Feed {}".format(repr(obj)))
        self.feeds.append(fed)
        session.add(fed)

        # SQLAQ - With Postgres, I don't need this commit here.
        # with SQLite, I do. On SQLite, if I don't have it, I get a really
        # strange situation where self.feeds can have two identical Feeds
        # matching, after only ever calling add_feed ONCE, on a brand new
        # SQLite file.
        session.commit()

    def add_alias(self, obj):
        if isinstance(obj, list):
            raise NotImplementedError
        elif isinstanceofany(obj, (str, unicode)):
            a = SymbolAlias(self, obj)
            self.aliases.append(a)
            session.add(a)

    def data(self):
        dtbl = self.datatable
        print type(dtbl)
        if isinstance(dtbl, Table):
            return session.query(dtbl.c.datetime, dtbl.c.final).all()
        else:
            raise Exception("Symbol has no datatable")

    @property
    def df(self):
        """ returns the dataframe representation of the symbol's final data """
        data = self.data()
        adf = pd.DataFrame(data)
        adf.columns = ['dateindex', self.name]
        adf = adf.set_index('dateindex')
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

    def add_validity(self, checkpoint, logic, kwargs):
        for key, value in kwargs.iteritems():
            self.validity.append(SymbolValidity(checkpoint=checkpoint,
                                                logic=logic,
                                                key=key,
                                                value=value,
                                                symbol=self))
        #self = session.merge(self)
        session.commit()

    def set_description(self, description):
        """ change the description of the symbol """
        self.description = description

    def set_freq(self, freq):
        """ change the frequency of the index """
        self.freq = freq

    def set_units(self, units):
        """ change the symbol's units """
        self.units = units

    def _init_datatable(self):
        """
        Instantiates the .datatable attribute, pointing to a table in the
        database that stores all the cached data
        """
        self.datatable = self._datatable_factory()
        self.datatable.drop(checkfirst=True)
        self.datatable.create()
        self.datatable_exists = True

    def _datatable_factory(self):
        """
        creates a SQLAlchemy Table object with the appropriate number of
        columns given the number of feeds
        """
        feed_cols = ['feed{0:03d}'.format(i + 1) for i in range(self.n_feeds)]
        feed_cols = ['override_feed000'] + feed_cols + ['failsafe_feed999']

        atbl = Table(self.name, metadata,
                     Column('datetime', DateTime, primary_key=True),
                     Column('final', Float),
                     *(Column(feed_col, Float) for feed_col in feed_cols),
                     extend_existing=True)
        return atbl


@event.listens_for(Symbol, 'load')
def __receive_load(target, context):
    """ loads a symbols data table upon being queried """
    target._init_datatable()


def set_symbol_or_symname(self,sym):
    if isinstance(sym, (str,unicode)):
        setattr(self,"symname",sym)
    else:
        setattr(self,"symbol",sym)

class SymbolTag(Base, ReprMixin):
    __tablename__ = '_symbol_tags'
    symname = Column('symname', String, ForeignKey('_symbols.name', **CC),
                     primary_key=True)
    tag = Column('tag', String, primary_key=True)

    symbol = relationship("Symbol")

    def __init__(self, tag, sym=None):
        set_symbol_or_symname(self,sym)
        self.tag = tag


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
    argint = Column('argint', Integer)
    argstr = Column('argstr', String)

    symbol = relationship("Symbol")

    def __init__(self, symbol, validator, argint=None, argstr=None):
        self.symbol = symbol

        self.validator = validator
        self.argint = argint
        self.argstr = argstr


class SymbolHandle(Base, ReprMixin):
    __tablename__ = "_symbol_handle"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    caching_of_feeds = Column('caching_of_feeds', BitFlagType)
    feed_aggregation_problem = Column('feed_aggregation_problem', BitFlagType)
    validity_check = Column('validity_check', BitFlagType)
    other = Column('other', BitFlagType)

    symbol = relationship("Symbol")

    def __init__(self, chkpnt_settings={}, sym=None):

        set_symbol_or_symname(self,sym)

        self.caching_of_feeds = BitFlag(0)
        self.feed_aggregation_problem = BitFlag(['stdout'])
        self.validity_check = BitFlag(['report'])
        self.other = BitFlag(['raise'])

        # override with anything passed in
        for checkpoint in chkpnt_settings:
            if checkpoint in SymbolHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self,checkpoint, settings)


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

    handle = relationship("FeedHandle", uselist=False, backref='_feeds', cascade=ADO)

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

        self._symsess = object_session(symbol)

        if fnum is None:
            qry = session.query(Feed.fnum)
            existing_fnums = qry.filter(Feed.symname == symbol.name).all()
            existing_fnums = [n[0] for n in existing_fnums]
            if len(existing_fnums) == 0:
                self.fnum = 0
            else:
                self.fnum = max(existing_fnums) + 1
        else:
            self.fnum = fnum

        def setinmeta(typ, infobj):
            """ moves information from infobj to meta """
            val = None
            if meta is not None and typ in meta:
                val = meta[typ]
                del meta[typ]
            # otherwise fall back to the value used in the sourcing dictionary.
            elif infobj is not None and typ in infobj:
                val = infobj[typ]
                del infobj[typ]

            if val:
                tmp = FeedMeta(attr=typ, value=val, feed=self)
                self._symsess.add(tmp)
                self.meta_map[typ] = tmp
                self._symsess.commit()

        setinmeta('stype', sourcing)
        setinmeta('sourcing_key', sourcing)

        if meta:
            for key in meta:
                tmp = FeedMeta(attr=key, value=meta[key], feed=self)
                self._symsess.add(tmp)
                self.meta_map[key] = tmp
                self._symsess.commit()

        if sourcing:
            for key in sourcing:
                tmp = FeedSource(param=key, value=sourcing[key], feed=self)
                self._symsess.add(tmp)
                self.sourcing_map[key] = tmp
                self._symsess.commit()

        if munging:
            for i, meth in enumerate(munging.keys()):
                print i, meth, munging[meth]
                fmg = FeedMunge(order=i, mtype=munging[meth]['mtype'],
                                method=meth, feed=self)
                for arg, value in munging[meth]['kwargs'].iteritems():
                    print arg, value
                    if not isinstance(value, (int, float)):
                        val = str(value)
                    else:
                        val = value
                    fmg.mungeargs.append(FeedMungeArg(arg, val, feedmunge=fmg))
                self.munging.append(fmg)

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
            db = __import__(engine.driver)
            con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}

            print kwargs
            print con_kwargs

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

        # munge accordingly
        for mgn in self.munging:
            print mgn.mtype
            mmkeys = mgn.munging_map.keys()
            kwargs = {k: mgn.munging_map[k].value for k in mmkeys}
            for arg in kwargs:
                if kwargs[arg].isnumeric():
                    tmp = float(kwargs[arg])
                    if (tmp % 1) == 0:  # then, probably an int.
                        kwargs[arg] = int(tmp)
                    else:
                        kwargs[arg] = tmp
                elif kwargs[arg].upper() == 'TRUE':
                    kwargs[arg] = True
                elif kwargs[arg].upper() == 'FALSE':
                    kwargs[arg] = False
            if mgn.mtype == pab:
                afunc = getattr(self.data, mgn.method)
                self.data = afunc(**kwargs)
            elif mgn.mtype == pnab:
                lib = __import__('pandas', globals(), locals(), [], -1)
                afunc = getattr(lib, mgn.method)
                self.data = afunc(self.data, **kwargs)

        # make sure it's named properly...
        self.data.name = "feed" + str(self.fnum + 1).zfill(3)

#            for a in mgn.methodargs:
#                args[a.arg] = a.value
#            self.data = munging_methods[mgn.method](self.data,**args)

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
    param = Column('param', String, primary_key=True)

    feed = relationship("Feed")

    value = Column('value', String)

    fkey = ForeignKeyConstraint([symname, fnum],
                                [Feed.symname, Feed.fnum],
                                **CC)
    __table_args__ = (fkey, {})

    def __init__(self, feed, param, value):
        self.feed = feed
        self.param = param
        self.value = value


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
    mungeargs = relationship("FeedMungeArg", lazy="dynamic", cascade=ADO)

    fkey = ForeignKeyConstraint([symname, fnum], [Feed.symname, Feed.fnum])
    __table_args__ = (fkey, {})

    def __init__(self, order, mtype, method, feed):
        self.order = order
        self.method = method
        self.mtype = mtype
        self.feed = feed

    @property
    def munging_map(self):
        return ProxyDict(self, 'mungeargs', FeedMungeArg, 'arg')


class FeedMungeArg(Base, ReprMixin):
    __tablename__ = "_feed_munging_args"

    symname = Column('symname', String, primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)
    order = Column('order', Integer, primary_key=True)
    arg = Column('arg', String, primary_key=True)
    value = Column('value', String)

    feedmunge = relationship("FeedMunge")

    fkey = ForeignKeyConstraint([symname, fnum, order],
                                [FeedMunge.symname,
                                 FeedMunge.fnum,
                                 FeedMunge.order])
    __table_args__ = (fkey, {})

    def __init__(self, arg, value, feedmunge):
        self.arg = arg
        self.value = value
        self.feedmunge = feedmunge

class FeedHandle(Base, ReprMixin):
    __tablename__ = "_feed_handle"

    symname = Column('symname', String, primary_key=True)
    fnum = Column('fnum', Integer, primary_key=True)

    api_failure = Column('api_failure', BitFlagType)
    empty_feed = Column('empty_feed', BitFlagType)
    index_type_problem = Column('index_type_problem', BitFlagType)
    index_property_problem = Column('index_property_problem', BitFlagType)
    data_type_problem = Column('data_type_problem', BitFlagType)
    non_monotonic = Column('non_monotonic', BitFlagType)
    other = Column('other', BitFlagType)

    feed = relationship("Feed")

    fkey = ForeignKeyConstraint([symname, fnum], [Feed.symname, Feed.fnum])
    __table_args__ = (fkey, {})

    def __init__(self, feed):
        self.feed = feed

        self.api_failure = BitFlag(['raise'])
        self.empty_feed = BitFlag(['stdout','report'])
        self.index_type_problem = BitFlag(['stdout','report'])
        self.index_property_problem = BitFlag(['stdout'])
        self.data_type_problem = BitFlag(['stdout','report'])
        self.non_monotonic = BitFlag(['raise'])
        self.other = BitFlag(['raised'])


class Override(Base, ReprMixin):
    __tablename__ = '_overrides'

    symname = Column('symname', String, primary_key=True)
    ornum = Column('ornum', Integer, primary_key=True)
    dt_ind = Column('dt_ind', DateTime, nullable=False)

    value = Column('value', Float, nullable=False)

    dt_log = Column('dt_log', DateTime, nullable=False)
    user = Column('user', String, nullable=True)
    comment = Column('comment', String, nullable=True)


class FailSafe(Base, ReprMixin):
    __tablename__ = '_failsafes'

    symname = Column('symname', String, primary_key=True)
    fsnum = Column('fsnum', Integer, primary_key=True)
    dt_ind = Column('dt_ind', DateTime, nullable=False)

    value = Column('value', Float, nullable=False)

    dt_log = Column('dt_log', DateTime, nullable=False)
    user = Column('user', String, nullable=True)
    comment = Column('comment', String, nullable=True)


try:
    Base.metadata.create_all(engine)
    print "Trump is ready."
except ProgrammingError as pgerr:
    print pgerr.statement
    print pgerr.message
    raise

if __name__ == '__main__':
    pass