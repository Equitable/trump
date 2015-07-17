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

from pdb import set_trace as bp
import datetime as dt
import json

from dateutil.relativedelta import relativedelta as rd

import pandas as pd
from sqlalchemy import event, Table, Column, ForeignKey, ForeignKeyConstraint,\
    String, Integer, Float, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, aliased
from sqlalchemy.orm.session import object_session
from sqlalchemy.exc import ProgrammingError, NoSuchTableError
from sqlalchemy.sql import and_, or_
from sqlalchemy import create_engine

from indexing import indexingtypes
from validity import validitychecks
from datadef import datadefs

from extensions.loader import sources

from trump.tools import ReprMixin, ProxyDict, isinstanceofany, \
    BitFlag, BitFlagType, ReprObjType, DuckTypeMixin, new_alchemy_encoder

from trump.aggregation.symbol_aggs import FeedAggregator, sorted_feed_cols
from trump.templating import bFeed, pab, pnab
from trump.options import read_config, read_settings
from trump.converting import FXConverter

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

try:
    MONICKER = read_config(sect='about', sett='monicker')
except:
    print ("Problem reading trump.cfg.  Continuing using the monicker"
           "defined in orm.py")
    MONICKER = "unknown"
    
rbd = read_config(sect='options', sett='raise_by_default')
if rbd.upper() == 'TRUE':
    rbd = BitFlag(1)
else:
    rbd = None


# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base = declarative_base()

ADO = "all, delete-orphan"
CC = {'onupdate': "CASCADE", 'ondelete': "CASCADE"}

class SymbolManager(object):

    """
    The SymbolManager maintains the SQLAlchemy database session, and 
    provides access to object creation, deletion, searching, and 
    overrides/failsafes.
    """

    def __init__(self, engine_or_eng_str=None, loud=False, echo=False):
        """
        Parameters
        ----------
        engine_or_eng_str : str or None, optional
            Pass a SQLAlchemy engine, or a string.  Without one,
            it will use the string provided in trump/options/trump.cfg
            If it fails to get a value there, an in-memory SQLlite
            session would be created.
        loud : bool, optional
            Print information such as engine string used, defaults to False
        echo : bool, optional
            If a new engine is created, it will pass this to it'safes
            constructor, enabling SQLAlchemy's echo mode.
            
        Returns
        -------
        SymbolManager
        """
        if engine_or_eng_str is None:
            engine = create_engine(ENGINE_STR, echo=echo)
        elif isinstance(engine_or_eng_str, (str, unicode)):
            engine = create_engine(engine_or_eng_str, echo=echo)
        else:
            engine = engine_or_eng_str
        
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        
        self.loud = loud
        if loud:
            print "Using engine: {}".format(ENGINE_STR)
        
        self.eng = engine

        self.ses = DBSession()
        
    def finish(self):
        """ Closes the session with the database.

        Call at the end of a trump session. It also 
        calls SessionManager.complete().
        """
        self.complete()
        self.ses.close()

    def create(self, name, description=None, units=None,
               agg_method="priority_fill", overwrite=False):
        """ Create, or get if exists, a Symbol.
        
        Parameters
        ----------
        name : str
            A symbol's name is a primary key, used across
            the Trump ORM.
        description : str, optional
            An arbitrary string, used to store user information
            related to the symbol.
        units : str, optional
            This is a string used to denote the units of the final
            data Series.
        agg_method : str, optional
            The aggregation method, used to calculate
            the final feed.  Defaults to priority_fill.
        overwrite : bool, optional
            Set to True, to force deletion an existing symbol.
            defaults to False.
            
        Returns
        -------
        Symbol
        """
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
        
        Parameters
        ----------
        symbol : str or Symbol
        """
        if isinstance(symbol, str):
            sym = self.get(symbol)
        elif isinstance(symbol, Symbol):
            sym = symbol
        else:
            raise Exception("Invalid symbol {}".format((repr(symbol))))

        # Has to handle the case where the table would exist already
        # and where it wouldn't.
        try:
            sym.datatable = Table(sym.name, Base.metadata, autoload=True)
            sym.datatable.drop(self.eng, checkfirst=True)
        except NoSuchTableError:
            print "No worries, {} never existed to begin with.".format(sym.name)

        self.ses.delete(sym)
        self.ses.commit()
        
    def complete(self):
        """Commits any changes to the database.
        In general, most of Trump API's auto-commits
        or does so internally.  
        
        This is necessary when working directly with SQLAlchemy
        exposed attributes.
        """
        self.ses.commit()

    def exists(self, symbol):
        """Checks to if a symbol exists, by name.
        
        Parameters
        ----------
        symbol : str or Symbol

        Returns
        -------
        bool
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
        """ Gets a Symbol based on name, which is expected to exist. 
        
        Parameters
        ----------
        symbol : str or Symbol
        
        Returns
        -------
        Symbol
        
        Raises
        ------
        Exception
            If it does not exist. Use .try_to_get(), 
            if the symbol may or may not exist.
        """
        syms = self.try_to_get(symbol)
        if syms is None:
            raise Exception("Symbol {} does not exist".format(symbol))
        else:
            return syms

    def try_to_get(self, symbol):
        """ Gets a Symbol based on name, which may or may not exist.
        
        Parameters
        ----------
        symbol : str
        
        Returns
        -------
        Symbol or None.  
        
        Note
        ----
        Use .get(), if the symbol should exist, and an exception 
        is needed if it doesn't.

        """
        syms = self.ses.query(Symbol).filter(Symbol.name == symbol).all()
        if len(syms) == 0:
            return None
        else:
            return syms[0]
    def existing_meta_attr(self):
        qry = self.ses.query(SymbolMeta.attr).order_by(SymbolMeta.attr)
        result = qry.distinct().all()
        return [res[0] for res in result]
    def search(self, usrqry=None, name=False, desc=False, tags=False, meta=False, stronly=False, dolikelogic=True):
        """ Get a list of Symbols by searching a combination of 
        a Symbol's name, description, tags or meta values.

        Parameters
        ----------
        usrqry : str
            The string used to query.  Appending '%' will use SQL's "LIKE"
            functionality.
        name : bool, optional, default False
            Search by symbol name.
        desc : bool, optional, default False
            Search by symbol descriptions.
        tags : bool, optional, default False
            Search by symbol tags.
        meta : bool, optional, default False
            Search within a symbol's meta attribute's value.
        stronly : bool, optional, default True
            Return only a list of symbol names, as opposed
            to the (entire) Symbol objects.
        dolikelogic : 
            Append '%' to either side of the string, if the string
            doesn't already have % specified.
        
        Returns
        -------
        List of Symbols or empty list
        
        """
        if stronly:
            qry = self.ses.query(Symbol.name)
        else:
            qry = self.ses.query(Symbol)

        if tags:
            qry = qry.join(SymbolTag)
        if meta:
            qry = qry.join(SymbolMeta)
        
        if dolikelogic:
            if usrqry is not None:
                if '%' not in usrqry:
                    usrqry = '%' + usrqry + '%'
        
        crits = []
        if name:
            crits.append(Symbol.name.like(usrqry))
        if tags:
            crits.append(SymbolTag.tag.like(usrqry))
        if desc:
            crits.append(Symbol.description.like(usrqry))
        if meta:
            crits.append(SymbolMeta.value.like(usrqry)) 
        
        if len(crits):
            qry = qry.filter(or_(*crits))
        
        qry = qry.order_by(Symbol.name)

        if stronly:
            return [sym[0] for sym in qry.distinct()]
        else:
            return [sym for sym in qry.distinct()]
    def search_tag(self, tag, symbols=True, feeds=False):
        """ Get a list of Symbols by searching a tag or partial tag.

        Parameters
        ----------
        tag : str
            The tag to search.  Appending '%' will use SQL's "LIKE"
            functionality.
        symbols : bool, optional
            Search for Symbol's based on their tags.
        feeds : bool, optional
            Search for Symbol's based on their Feeds' tags.
        
        Returns
        -------
        List of Symbols or empty list
        
        """

        syms = []
        
        if isinstance(tag, (str, unicode)):
            tags = [tag]
        else:
            tags = tag

        if symbols:
            crits = []
            for tag in tags:
                if "%" in tag:
                    crit = SymbolTag.tag.like(tag)
                else:
                    crit = SymbolTag.tag == tag
                crits.append(crit)

            qry = self.ses.query(SymbolTag)
            qry = qry.filter(or_(*crits))
            syms = qry.all()
            
            syms = [tagged.symbol for tagged in syms]
        if feeds:
            crits = []
            for tag in tags:
                if "%" in tag:
                    crit = FeedTag.tag.like(tag)
                else:
                    crit = FeedTag.tag == tag
                crits.append(crit)
                    
            qry = self.ses.query(Symbol).select_from(FeedTag)
            qry = qry.join(FeedTag.feed).join(Feed.symbol)
            qry = qry.filter(or_(*crits))
            fds = qry.distinct()
            
            syms = syms + [sym for sym in fds]
            return list(set(syms))
        return syms

    def search_meta(self, **avargs):
        """Search list of Symbol objects by by querying specific 
        meta attributes and their respective values.
        
        Parameters
        ----------
        avargs
            The attributes and values passed as key word arguments.
            If more than one criteria is specified, AND logic is applied.
            Appending '%' to values will use SQL's "LIKE" functionality.
        
        Example
        -------
        >>> sm.search_meta(geography='Canada', sector='Gov%')
            
        Returns
        -------
        List of Symbols or empty list
        """
        
        qry = self.ses.query(Symbol).join(SymbolMeta.symbol)


        for attr, value in avargs.iteritems():
            SMA = aliased(SymbolMeta)
            if "%" in value:
                acrit = SMA.value.like(value)
            else:
                acrit = SMA.value == value
            
            crit = and_(acrit, SMA.attr == attr)

            qry = qry.filter(crit).join(SMA, SMA.symname == SymbolMeta.symname)

        qry = qry.order_by(Symbol.name)
        return qry.all()

    def bulk_cache_of_tag(self, tag):
        """ Caches all the symbols by a certain tag.

        For now, there is no different, than 
        caching each symbol individually.  In the future,
        this functionality could have speed improvements.

        Parameters
        ----------
        tag : str
            Use '%' to enable SQL's "LIKE" functionality.

        Returns
        -------
        TrumpReport
        """

        syms = self.search_tag(tag)
        
        name = 'Bulk Cache of Symbols tagged {}'.format(tag)
        tr = TrumpReport(name)
        for sym in syms:
            sr = sym.cache()
            tr.add_symbolreport(sr)
        
        return tr
        
    def build_view_from_tag(self, tag):
        """
        Build a view of group of Symbols based on their tag.
        
        Parameters
        ----------
        tag : str
            Use '%' to enable SQL's "LIKE" functionality.
        
        Note
        ----
        
        This function is written without SQLAlchemy,
        so it only tested on Postgres.

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
    def add_existing_ind_orfs(self, which, symbol, orfs_n, value, comment=None, user=None):
        ind = self.ses.query(symbol.datatable.c.indx).order_by(symbol.datatable.c.indx).offset(orfs_n).limit(1).one()
        ind = ind[0]
        tmp = {'or' : 'override', 'fs' : 'failsafe'}
        self._add_orfs(tmp[which], symbol, ind, value, user=user, comment=comment)
    def _add_orfs(self, which, symbol, ind, val, dt_log=None, user=None, comment=None):
        """
        Appends a single indexed-value pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        See add_override and add_fail_safe.
        
        Parameters
        ----------
        which : str
            Fail Safe or Override?
        symbol : Symbol or str
            The Symbol to apply the fail safe
        ind : obj
            The index value where the fail safe should be applied
        val : obj
            The data value which will be used in the fail safe
        dt_log : datetime
            A log entry, for saving when this fail safe was created.
        user : str
            A string representing which user made the fail safe
        comment : str
            A string to store any notes related to this fail safe.
        """
        if not isinstance(symbol, (str, unicode)):
            symbol = symbol.name

        if not dt_log:
            dt_log = dt.datetime.now()

        if which.lower() == 'override':
            qry = self.ses.query(func.max(Override.ornum).label('max_ornum'))
            override = True
        elif which.lower() == 'failsafe':
            qry = self.ses.query(func.max(FailSafe.fsnum).label('max_fsnum'))
            override = False
            
        qry = qry.filter_by(symname = symbol)
        
        cur_num = qry.one()
        
        if cur_num[0] is None:
            next_num = 0
        else:
            next_num = cur_num[0] + 1            

        if override:
            tmp = Override(symname=symbol,
                           ind=ind,
                           val=val,
                           dt_log=dt_log,
                           user=user,
                           comment=comment,
                           ornum=next_num)
        else:
            tmp = FailSafe(symname=symbol,
                           ind=ind,
                           val=val,
                           dt_log=dt_log,
                           user=user,
                           comment=comment,
                           fsnum=next_num)
                                             
        self.ses.add(tmp)
        self.ses.commit()
        
    def add_override(self, symbol, ind, val, dt_log=None, user=None, comment=None):
        """
        Appends a single indexed-value pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        With default settings Overrides, get applied with highest priority.
        
        Parameters
        ----------
        symbol : Symbol or str
            The Symbol to override
        ind : obj
            The index value where the override should be applied
        val : obj
            The data value which will be used in the override
        dt_log : datetime
            A log entry, for saving when this override was created.
        user : str
            A string representing which user made the override
        comment : str
            A string to store any notes related to this override.
        """
        self._add_orfs('override', symbol, ind, val, dt_log, user, comment)


    def add_fail_safe(self, symbol, ind, val,
                      dt_log=None, user=None, comment=None):
        """
        Appends a single indexed-value pair, to a symbol object, to be
        used during the final steps of the aggregation of the datatable.

        With default settings FailSafes, get applied with lowest priority.
        
        Parameters
        ----------
        symbol : Symbol or str
            The Symbol to apply the fail safe
        ind : obj
            The index value where the fail safe should be applied
        val : obj
            The data value which will be used in the fail safe
        dt_log : datetime
            A log entry, for saving when this fail safe was created.
        user : str
            A string representing which user made the fail safe
        comment : str
            A string to store any notes related to this fail safe.
        """
        self._add_orfs('failsafe', symbol, ind, val, dt_log, user, comment)
        
    def delete_orfs(self, sym, which, orfs_num):
        if which.lower() in ('or', 'override'):
            crit = and_(Override.ornum == orfs_num, Override.symname == sym)
            qry = self.ses.query(Override)
        elif which.lower() in ('fs', 'failsafe'):
            crit = and_(FailSafe.fsnum == orfs_num, FailSafe.symname == sym)
            qry = self.ses.query(FailSafe)
        else:
            raise Exception("{} is not or/override or fs/failsafe".format(which))
        qry.filter(crit).delete(synchronize_session=False)
        self.ses.commit()
        
class ConversionManager(SymbolManager):
    """
    A ConversionManager handles the conversion of previously instantiated
    symbols, based on the object's units and the conversion manager
    setup.  The conversion is performed adhoc, in python
    only usage.  That is, nothing about the conversion persists
    in the Trump framework.  Only the final series is converted.
    """
    def __init__(self, engine_or_eng_str=None, system='FX', tag=None):
        """
        Parameters
        ----------
        engine_or_eng_str : str or None
            Pass a SQLAlchemy engine, or a string.  Without one,
            it will use the defaul provided in trump/options/trump.cfg
            If it fails to get a value there, an in-memory SQLlite
            session would be created.
        system : str, optional
            Uses the FX conversion system logic by default.
            Currently, no other systems are implemented.  Eg. metric-only,
            imperial-metric, etc.
            
            Other systems can be added after instantiation of the
            ConversionManager, but the one specified at instantiation
            will be used as default.
            
        tag : str, optional
            Tag for the set of feeds to use for conversion.  Only necessary,
            if the conversion system relies on it.  For FX, it's needed, to 
            specify the set of feeds to use.       

            Other tags can be added after instantiation of the
            ConversionManager, but the one specified at instantiation
            will be used as default.

        """
        super(ConversionManager, self).__init__(engine_or_eng_str)
        
        self.default_system = system
        self.default_tag = tag
        
        self.converters = {}
        self.add_converter(system, tag)

    def add_converter(self, system, tag):
        if system not in self.converters:
            self.converters[system] = {}
            
        if tag not in self.converters[system]:
            if system == 'FX':
                if tag is None:
                    raise Exception("Must specify a tag for FX Conversion")
                conversion_syms = self.search_tag(tag)
                conv = FXConverter()
                conv.use_trump_data(conversion_syms)
                self.converters[system][tag] = conv
                
    def get_converted(self, symbol, units='CAD', system=None, tag=None):
        """
        Uses a Symbol's Dataframe, to build a new Dataframe,
        with the data converted to the new units
        
        Parameters
        ----------
        symbol : str or tuple of the form (Dataframe, str)
            String representing a symbol's name, or a dataframe
            with the data required to be converted.  If supplying a 
            dataframe, units must be passed.
        units : str, optional
            Specify the units to convert the symbol to, default to CAD 
        system : str, optional
            If None, the default system specified at instantiation
            is used.  System defines which conversion approach to take.
        tag : str, optional
            Tags define which set of conversion data is used.  If None, the
            default tag specified at instantiation is used.  
        """
        if isinstance(symbol, (str, unicode)):
            sym = self.get(symbol)
            df = sym.df
            curu = sym.units
            requ = units
        elif isinstance(symbol, tuple):
            df = symbol[0]
            curu = symbol[1]
            requ = units
        else:
            raise TypeError("Expected str or (DataFrame, str), found {}".format(type(symbol)))
        
        system = system or self.default_system
        tag = tag or self.default_tag
        
        conv = self.converters[system][tag]

        newdf = conv.convert(df, curu, requ)
        newdf = pd.merge(df, newdf, left_index=True, right_index=True)
        newdf = newdf[df.columns[0] + "_y"].to_frame()
        newdf.columns = df.columns
        return newdf
        
class Symbol(Base, ReprMixin):
    __tablename__ = '_symbols'

    name = Column('name', String, primary_key=True)
    description = Column('description', String)
    units = Column('units', String)
    agg_method = Column('agg_method', String)
    
    #minutes since last cache
    freshthresh = Column('freshthresh', Integer, default=0)

    log = relationship('SymbolLogEvent', lazy="dynamic", backref='_symbols', cascade=ADO)
                         
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
    meta = relationship("SymbolMeta", lazy='dynamic', cascade=ADO)
    
    def __init__(self, name, description=None, units=None,
                 agg_method="PRIORITY_FILL",
                 indexname="UNNAMED", indeximp="DatetimeIndexImp",
                 freshthresh=0):
        """A Trump Symbol persistently objectifies indexed data

        Use the SymbolManager class to create or retrieve existing symbols.

        Parameters
        ----------
        name : str
            The name of the symbol to be added to the database, serves
            as a primary key across the trump installation.
        description : str, optional
            a description of the symbol, just for notes.
        units : str, optional
            a string representing the units for the data.
        agg_method : str, default PRIORITY_FILL
            the method used for aggregating feeds, see
            trump.aggregation.symbol_aggs.py for the list of available options.
        indexname : str
            a proprietary name assigned to the index.
        indeximp : str
            a string representing an index implementer (one of the classes in indexing.py)
        freshthresh : int, default 0
            number of minutes before the feed is considered stale.

        """
        
        self.name = name
        self.description = description
        self.units = units
        self.freshthresh = freshthresh

        self.index = Index(indexname, indeximp, sym=name)
        self.dtype = SymbolDataDef("SkipDataDef", sym=name)
        
        self.agg_method = agg_method
        self.datatable = None
        self.datatable_exists = False
    def to_json(self):
        return json.dumps(self, cls=new_alchemy_encoder(), check_circular=False)
    def last_cache(self,result='COMPLETE'):
        """
        returns datetime
        """
        crit = and_(SymbolLogEvent.event == 'CACHE',
                    SymbolLogEvent.evresult == result)
        qry = self.log.filter(crit)
        qry = qry.order_by(SymbolLogEvent.evtime.desc())
        
        t = qry.first()
        
        if t:
            return t.evtime
        else:
            return None
            
    def set_indexing(self, index_template):
        """
        Update a symbol's indexing strategy
        
        Parameters
        ----------
        index_template : bIndex or bIndex-like
            An index template used to overwrite all 
            details about the symbol's current index.

        """
        objs = object_session(self)
        
        if self.index.indimp != index_template.imp_name:
            self._refresh_datatable_schema()
        
        self.index.name = index_template.name
        self.index.indimp = index_template.imp_name
        self.index.case = index_template.case
        self.index.setkwargs(**index_template.kwargs)
        objs.commit()

    def add_meta(self, **metadict):
        """Add meta information to a Symbol.
                
        Parameters
        ----------
        metadict 
            Attributes are passed as keywords, with their
            associated values as strings.  For meta attributes with spaces,
            use an unpacked dict.
                    
        """
        
        objs = object_session(self)
        
        for attr,val in metadict.iteritems():
            newmeta = SymbolMeta(self, attr, val)
            self.meta.append(newmeta)
            
        objs.commit() 
        
    def add_validator(self, val_template):
        """
        Creates and adds a SymbolValidity object to the Symbol.

        Parameters
        ----------
        validity_template : bValidity or bValidity-like
            a validity template.

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

        Parameters
        ----------
        chkpnt_settings : dict
            a dictionary where the keys are stings representing
            individual handle checkpoint names, for a Symbol
            (eg. caching_of_feeds, feed_aggregation_problem, ...)
            See SymbolHandle.__table__.columns for the
            current list.

            The values can be either integer or BitFlags.
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

    def cache(self, checkvalidity=True, staleonly=False, allowraise=True):
        """ Re-caches the Symbol's datatable by querying each Feed. 
        
        Parameters
        ----------
        checkvalidity : bool, optional
            Optionally, check validity post-cache.  Improve speed by
            turning to False.
        staleonly : bool, default False
            Set to True, for speed up, by looking at staleness
        allowraise : bool, default True
            AND with the Symbol.handle and Feed.handle's 'raise',
            set to False, to do a list of symbols.  Note, this
            won't silence bugs in Trump, eg. unhandled edge cases.
            So, those still need to be handled by the application.
        
        Returns
        -------
        SymbolReport
        """
        note = "staleonly = {}".format(staleonly)
        self._log_an_event('CACHE','START',note)

        docache = True
        if staleonly:
            lc = self.last_cache()
            if lc:
                freshthresh = self.freshthresh 
                
                nw = dt.datetime.now()
                freshness = (nw - lc).total_seconds() / 60.0

                if freshness <= freshthresh:
                    docache = False
        
        smrp = SymbolReport(self.name)
        if docache:
            data = []
            cols = ['final', 'override_feed000', 'failsafe_feed999']
    
            if len(self.feeds) == 0:
                err_msg = "Symbol has no Feeds. Can't cache a feed-less Symbol."
                raise Exception(err_msg)
    
            try:
                datt = datadefs[self.dtype.datadef]
                
                rp = ReportPoint('datadef', 'class', datt)
                smrp.add_reportpoint(rp)
                
                for afeed in self.feeds:
                    fdrp = afeed.cache(allowraise)
                    smrp.add_feedreport(fdrp)
                    tmp = datt(afeed.data).converted
                    data.append(tmp)
                    cols.append(afeed.data.name)
            except:
                point = "caching"
                smrp = self._generic_exception(point, smrp, allowraise)
                    
            try:
                data = pd.concat(data, axis=1)
            except:
                point = "concatenation"
                smrp = self._generic_exception(point, smrp, allowraise)
            
            preindlen = len(data)
            indtt = indexingtypes[self.index.indimp]
            indkwargs = self.index.getkwargs()
            
            if preindlen > 0 : 
                indt = indtt(data, self.index.case, indkwargs)
                data = indt.final_dataframe()

                postindlen = len(data)   
                if postindlen == 0 and preindlen > 0:
                    raise Exception("Indexing Implementer likely poorly designed")
            else:
                postindlen = 0
            
            
            def build_hi_df(which, colname):
                
                objs = object_session(self)
    
                qry = objs.query(which.ind,
                                 func.max(which.dt_log).label('max_dt_log'))
                
                qry = qry.filter_by(symname = self.name)
                
                grb = qry.group_by(which.ind).subquery()
        
                qry = objs.query(which)
                ords = qry.join((grb, and_(which.ind == grb.c.ind,
                                           which.dt_log == grb.c.max_dt_log))).all()
            
                if len(ords):
                    orind = [row.ind for row in ords]
                    orval = [row.val for row in ords]
                    ordf = pd.DataFrame(data=orval, index=orind, columns=[colname])
                    indt = indtt(ordf, self.index.case, indkwargs)
                    ordf = indt.final_dataframe()
                else:
                    ordf = pd.DataFrame(columns=[colname])
                return ordf
            
            ordf = build_hi_df(Override, 'override_feed000')
            fsdf = build_hi_df(FailSafe, 'failsafe_feed999')
            
            orfsdf = pd.merge(ordf, fsdf, how='outer', left_index=True, right_index=True)
            data = pd.merge(orfsdf, data, how='outer', left_index=True, right_index=True)

            try:
                data = data.fillna(value=pd.np.nan)
                data = data[sorted_feed_cols(data)]
                data['final'] = FeedAggregator(self.agg_method).aggregate(data)
            except:
                point = "aggregation"
                smrp = self._generic_exception(point, smrp, allowraise)
    
    
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
            
            if len(data) > 0:
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
                    smrp = self._generic_exception(point, smrp, allowraise)
            self._log_an_event('CACHE','COMPLETE', "Fresh!")
        else:
            self._log_an_event('CACHE','FRESH', "Was still fresh")
        return smrp          

    def check_validity(self, checks=None, report=True):
        """ Runs a Symbol's validity checks.
        
        Parameters
        ----------
        checks : str, [str,], optional
            Only run certain checks.  
        report : bool, optional
            If set to False, the method will return only the result of the
            check checks (True/False).  Set to True, to have a 
            SymbolReport returned as well.
            
        Returns
        -------
        Bool, or a Tuple of the form (Bool, SymbolReport)
        """        
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
        """Quick access to the results of a a check_validity report
        
        Returns
        -------
        Bool
        """
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
        """ remove a tag or tags from a symbol 
        
        Parameters
        ----------
        tags : str or [str,]
            Tags to be removed
        """
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
        """ add a tag or tags to a symbol
        
        Parameters
        ----------
        tags : str or [str,]
            Tags to be added
        """
        # SQLA Adding a SymbolTag object, feels awkward/uneccessary.
        # Should I be implementing this functionality a different way?

        if isinstance(tags, (str, unicode)):
            tags = [tags]

        objs = object_session(self)
        tmps = [SymbolTag(tag=t, sym=self) for t in tags]
        objs.add_all(tmps)
        objs.commit()

    def _log_an_event(self, event, evresult='No Result', note='No Note'):
        """ log an event
        
        Parameters
        ----------
        event : string
        evresult : string
        note : string
        """
        objs = object_session(self)
        evnt = SymbolLogEvent(event, evresult, note, sym=self.name)
        objs.add(evnt)
        objs.commit()
    @property
    def n_tags(self):
        """ returns the number of tags """
        return len(self.tags)

    def add_feed(self, feedlike, **kwargs):
        """ Add a feed to the Symbol
        
        Parameters
        ----------
        feedlike : Feed or bFeed-like
            The feed template, or Feed object to be added.
        kwargs
            Munging instructions
        """
        if 'fnum' in kwargs:
            fnum = kwargs['fnum']
            del kwargs['fnum']
        else:
            fnum = None

        if isinstance(feedlike, bFeed):
            munging = feedlike.munging
            if 'munging' in kwargs:
                explicit_munging = kwargs['munging'].as_odict
                for key in explicit_munging:
                    munging[key] = explicit_munging[key]
            fed = Feed(self, feedlike.ftype,
                       feedlike.sourcing,
                       munging,
                       feedlike.meta,
                       fnum)

        elif isinstance(feedlike, Feed):
            fed = feedlike
        else:
            raise Exception("Invalid Feed {}".format(repr(feedlike)))
        self.feeds.append(fed)
        
        objs = object_session(self)
        objs.add(fed)
        objs.commit()

    def add_alias(self, alias):
        """ Add an alias to a Symbol
        
        Parameters
        ----------
        alias : str
            The alias
        """
        objs = object_session(self)
        
        if isinstance(alias, list):
            raise NotImplementedError
        elif isinstanceofany(alias, (str, unicode)):
            a = SymbolAlias(self, alias)
            self.aliases.append(a)
            objs.add(a)

    def _final_data(self):
        """
        Returns
        -------
        A list of tuples representing rows from the datatable's index
        and final column, sorted accordingly.
        """
        dtbl = self.datatable

        objs = object_session(self)
        if isinstance(dtbl, Table):
            return objs.query(dtbl.c.indx, dtbl.c.final).all()
        else:
            raise Exception("Symbol has no datatable, likely need to cache first.")

    def _max_min(self):
        """
        Returns
        -------
        A tuple consisting of (max, min) of the index.
        """
        dtbl = self.datatable

        objs = object_session(self)
        if isinstance(dtbl, Table):
            return objs.query(func.max(dtbl.c.indx).label("max_indx"),
                              func.min(dtbl.c.indx).label("min_indx")).one()
        else:
            raise Exception("Symbol has no datatable")
            
    def _all_datatable_data(self):
        """
        Returns
        -------
        A list of tuples representing rows from all columns of the datatable,
        sorted accordingly.
        """
        dtbl = self.datatable
        objs = object_session(self)
        imcols = [dtbl.c.indx, dtbl.c.final, dtbl.c.override_feed000, dtbl.c.failsafe_feed999]
        cols = imcols[:3] + [c for c in dtbl.c if c not in (imcols)] + [imcols[3]]
        if isinstance(dtbl, Table):
            return objs.query(*cols).order_by(dtbl.c.indx).all()
        else:
            raise Exception("Symbol has no datatable")

    @property
    def df(self):
        """
        Note: this accessor is read-only.  It should be copied, if accessed in
        an application, more than once.
        
        Returns
        -------
            Dataframe of the symbol's final data.
        """
        data = self._final_data()
        
        if len(data) == 0:
            adf = pd.DataFrame(columns = [self.index.name, self.name])
            return adf.set_index(self.index.name)
            
        adf = pd.DataFrame(data)
        
        if len(adf.columns) != 2:
            msg = "Symbol ({}) needs to be cached prior to building a Dataframe"
            msg = msg.format(self.name)
            raise Exception(msg)
        adf.columns = [self.index.name, self.name]
        
        datt = datadefs[self.dtype.datadef]       
        adf[self.name] = datt(adf[self.name]).converted
        
        adf = adf.set_index(self.index.name)

        indt = indexingtypes[self.index.indimp]
        indt = indt(adf, self.index.case, self.index.getkwargs())
        adf = indt.final_series()

        if adf.index.name == "UNNAMED":
            adf.index.name = None

        return adf

    @property
    def datatable_df(self):
        """ returns the dataframe representation of the symbol's final data """
        data = self._all_datatable_data()
        adf = pd.DataFrame(data)
        
        adf.columns = self.dt_all_cols
        
        datt = datadefs[self.dtype.datadef]
        
        for col in adf.columns:
            adf[col] = datt(adf[col]).converted
        
        adf = adf.set_index('indx')

        indt = indexingtypes[self.index.indimp]
        indt = indt(adf, self.index.case, self.index.getkwargs())
        adf = indt.raw_data()
        
        if adf.index.name == "UNNAMED":
            adf.index.name = None
        else:
            adf.index.name = self.index.name
            
        return adf
        
    def del_feed(self):
        """ remove a feed """
        raise NotImplementedError("Feed deletion has not be created yet")

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
    def _generic_exception(self, point, reporter, allowraise=True):
        logic = getattr(self.handle, point).asdict()
        logic['raise'] = logic['raise'] and allowraise
        logic = BitFlag(logic)
        msg = "Exception at the point of {} for {}"
        msg = msg.format(point, self.name)
        hdlrp = Handler(logic, point, msg).process()
        if hdlrp:
            reporter.add_handlepoint(hdlrp)
        return reporter
    @property
    def meta_map(self):
        return ProxyDict(self, 'meta', SymbolMeta, 'attr')
    def existing_orfs(self):
        objs = object_session(self)
        
        #.order_by(Override.ornum.desc())
        ors = objs.query(Override).filter(Override.symname == self.name).order_by(Override.ornum.asc()).all()
        
        #.order_by(FailSafe.fsnum.desc())
        fss = objs.query(FailSafe).filter(FailSafe.symname == self.name).order_by(FailSafe.fsnum.asc()).all()
        
        return {'or' : ors, 'fs' : fss}
        
@event.listens_for(Symbol, 'load')
def __receive_load(target, context):
    """ loads a symbols datatable upon being queried """
    target._init_datatable()


def set_symbol_or_symname(self, sym):
    if isinstance(sym, (str, unicode)):
        setattr(self, "symname", sym)
    else:
        setattr(self, "symbol", sym)

class SymbolLogEvent(Base, ReprMixin):
    __tablename__ = '_symbol_log_events'
    evtime = Column('evtime', DateTime, primary_key=True)
    symname = Column('symname', String, ForeignKey('_symbols.name', **CC),
                     primary_key=True)

    event = Column('event', String)
    evresult = Column('evresult', String)
    monicker = Column('monicker', String)
    note = Column('note', String)
    
    def __init__(self, event, evresult='No Result', note='No Note', sym=None):
        set_symbol_or_symname(self, sym)
        self.event = event
        self.evresult = evresult
        self.monicker = MONICKER
        self.note = note
        self.evtime = dt.datetime.now()
        
class SymbolTag(Base, ReprMixin):
    __tablename__ = '_symbol_tags'
    symname = Column('symname', String, ForeignKey('_symbols.name', **CC),
                     primary_key=True)
    tag = Column('tag', String, primary_key=True)

    symbol = relationship("Symbol")

    def __init__(self, tag, sym=None):
        set_symbol_or_symname(self, sym)
        self.tag = tag

class SymbolMeta(Base, ReprMixin):
    __tablename__ = "_symbol_meta"

    symname = Column('symname', String, ForeignKey("_symbols.name", **CC),
                     primary_key=True)

    attr = Column('attr', String, primary_key=True)
    value = Column('value', String)

    symbol = relationship("Symbol")

    def __init__(self, symbol, attr, value):
        self.symbol = symbol
        self.attr = attr
        self.value = value

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
    Stores instructions about how to handle exceptions thrown
    during specific points of Symbol caching:

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

    def __init__(self, chkpnt_settings=None, sym=None):
        """
        
        Parameters
        ----------
        chkpnt_settings : dict
            A dictionary with keys matching names of the handle points
            and the values either integers or BitFlags
        sym : str or Symbol
            The Symbol that this SymbolHandle is associated with it.
        """
        set_symbol_or_symname(self, sym)

        self.caching = rbd or BitFlag(0)
        self.concatenation = rbd or BitFlag(['raise'])
        self.aggregation = rbd or BitFlag(['stdout'])
        self.validity_check = rbd or BitFlag(['report'])
        
        chkpnt_settings = chkpnt_settings or {}
        # override with anything passed in settings
        for checkpoint in chkpnt_settings:
            if checkpoint in SymbolHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self, checkpoint, settings)
    def setting(self, handlepoint):
        return getattr(self, handlepoint)
    @property
    def points(self):
        pnts = [str(p).split(".")[1] for p in SymbolHandle.__table__.columns if 'symname' not in str(p)]
        return [(pnt, getattr(self, pnt)) for pnt in pnts]

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

    def __init__(self, name, indimp, case=None, kwargs=None, sym=None):

        set_symbol_or_symname(self, sym)

        self.name = name
        self.indimp = indimp
        self.case = case or "asis"
        kwargs = kwargs or {}
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
    def add_tags(self, tags):
        """ add a tag or tags to a Feed """

        if isinstance(tags, (str, unicode)):
            tags = [tags]

        objs = object_session(self)
        tmps = [FeedTag(tag=t, feed=self) for t in tags]
        objs.add_all(tmps)
        objs.commit()

    def cache(self, allowraise):
        
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

            if stype in sources:
                self.data = sources[stype](self.ses, **kwargs)        
            else:
                raise Exception("Unknown Source Type : {}".format(stype))
            
        except:
            point = "api_failure"
            fdrp = self._generic_exception(point, fdrp, allowraise)
            self.data = pd.Series()

        try:
            if len(self.data) == 0 or self.data.empty:
                raise Exception('Feed is empty')
        except:
            point = "empty_feed"
            fdrp = self._generic_exception(point, fdrp, allowraise)

        try:
            if not (self.data.index.is_monotonic and self.data.index.is_unique):
                dtstr = str(self.data)
                indstr = str(self.data.index)
                msg = 'Feed index is not uniquely monotonic:' + dtstr + indstr
                raise Exception(msg)
        except:
            point = "monounique"
            fdrp = self._generic_exception(point, fdrp, allowraise)

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

    @property
    def meta_map(self):
        return ProxyDict(self, 'meta', FeedMeta, 'attr')

    @property
    def source(self):
        return " ".join([p.key + " : " + p.value for p in self.sourcing])
    def _generic_exception(self, point, reporter, allowraise=True):
        logic = getattr(self.handle, point).asdict()
        logic['raise'] = logic['raise'] and allowraise
        logic = BitFlag(logic)
        msg = "Exception for feed #{} for {} at the {} point."
        msg = msg.format(self.fnum, self.symname, point)
        hdlrp = Handler(logic, point, msg).process()
        if hdlrp:
            reporter.add_handlepoint(hdlrp)
        return reporter
    def _note_session(self):
        self.ses = object_session(self)

@event.listens_for(Feed, 'load')
def __receive_load(target, context):
    """ saves the session upon being queried """
    target._note_session()

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
    def __init__(self, tag, feed=None):
        self.feed = feed
        self.tag = tag

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

    def __init__(self, chkpnt_settings=None, feed=None):
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
        
        chkpnt_settings = chkpnt_settings or {}
        
        # override with anything passed in settings
        for checkpoint in chkpnt_settings:
            if checkpoint in FeedHandle.__table__.columns:
                settings = chkpnt_settings[checkpoint]
                setattr(self, checkpoint, settings)
    def setting(self, handlepoint):
        return getattr(self, handlepoint)
    @property
    def points(self):
        exclude = ['symname', 'fnum']
        pnts = [str(p).split(".")[1] for p in FeedHandle.__table__.columns if not any((ex in str(p) for ex in exclude))]
        return [(pnt, getattr(self, pnt)) for pnt in pnts]


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

