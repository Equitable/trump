# -*- coding: utf-8 -*-

###############################################################################
#
# PyLint tests that will never be applied by Trump.
#
# Used * or ** magic, we're not getting rid of this, this is what makes Trump
#                     possible
# pylint: disable-msg=W0142

# Abstract class not referenced, ignored because inheritance is useful info.
# pylint: disable-msg=R0921

# Too many/few arguments, ignored because its confusing and doesn't make
#                         sense to refactor templates.
#
# pylint: disable-msg=R0913
# pylint: disable-msg=R0903


"""
Trump's templating system consists of pure-python objects, which can
be converted into either lists, dictionaries, or ordered dictionaries,
which can then be used in the generalized constructors of Trump's SQLAlchemy
based ORM system.
"""

from trump.templating.bases import bTags, bMunging, bSource, bFeed, bIndex, \
                                   bValidity

from trump.options import read_settings

# *****************************************************************************
#
#  Tag Templates
#
# Tag Templates are any object which implements a property called
# as_list, which returns a list of strings
#
# *****************************************************************************

class AssetTT(bTags):
    """ implements groups of tags for certain asset classes """
    def __init__(self, cls):
        if cls.lower() in ('equity', 'stock', 'equities', 'stocks'):
            self.equity = True
        elif cls.lower() in ('bond', 'bonds'):
            self.bond = True
        elif cls.lower() in ('pref', 'preferred', 'preferred', 'prefered'):
            self.pref = True
        elif cls.lower() in ('comodity', 'commodity', 'commodities'):
            self.commodity = True

class GenericTT(bTags):
    """ implements generic list of tags via boolean attributes """
    def __init__(self, tags):
        for tag in tags:
            self.__setattr__(self, tag, True)

class SimpleTT(bTags):
    """ implements a simple list of tags via a single attribute """
    def __init__(self, tags):
        self.tags = tags

    def as_list(self):
        return self.tags

# *****************************************************************************
#
#   Munging Templates
#
#  Munging Templates are any object which implements a property called
#  as_odict, which returns an odict where each key is a function in
#  munging_methods, and it's value is an object which represents the parameters
#  to use on that object.  This should be sufficient to pass to a
#  a Feed constructor's munging parameter, which then becomes FeedMungingArgs
#  objects making up a FeedMunge object, of which will be the instructions
#  associated with a specific Feed object.
#
# *****************************************************************************

from trump.templating.munging_helpers import mixin_pab, mixin_pnab

class AbsMT(bMunging, mixin_pab):
    """ Example munging template, which implements an absolute function."""
    def __init__(self):
        super(AbsMT, self).__init__()
        self._bld_abs()

class RollingMeanMT(bMunging, mixin_pnab):
    """ Example munging template, which implements a rolling mean."""
    def __init__(self, **kwargs):
        super(RollingMeanMT, self).__init__()
        self._bld_rolling_mean(**kwargs)

class PctChangeMT(bMunging, mixin_pab):
    """ Example munging template, which implements pct_change."""
    def __init__(self, **kwargs):
        super(PctChangeMT, self).__init__()
        self._bld_pct_change(**kwargs)

class AsFreqMT(bMunging, mixin_pab):
    """ Example munging template, which implements pct_change."""
    def __init__(self, **kwargs):
        super(AsFreqMT, self).__init__()
        self._bld_asfreq(**kwargs)

class AddMT(bMunging, mixin_pab):
    """ Example munging template, which implements addition."""
    def __init__(self, num, **kwargs):
        super(AddMT, self).__init__()
        self._bld_op('add', num, **kwargs)

class SubMT(bMunging, mixin_pab):
    """ Example munging template, which implements subtraction."""
    def __init__(self, num, **kwargs):
        super(SubMT, self).__init__()
        self._bld_op('sub', num, **kwargs)

class MulMT(bMunging, mixin_pab):
    """ Example munging template, which implements multiplication."""
    def __init__(self, num, **kwargs):
        super(MulMT, self).__init__()
        self._bld_op('mul', num, **kwargs)

class DivMT(bMunging, mixin_pab):
    """ Example munging template, which implements division."""
    def __init__(self, num, **kwargs):
        super(DivMT, self).__init__()
        self._bld_op('div', num, **kwargs)
        
class PowerMT(bMunging, mixin_pab):
    """ Example munging template, which implements pct_change."""
    def __init__(self, num, **kwargs):
        super(PowerMT, self).__init__()
        self._bld_op('pow', num, **kwargs)
        
class FFillRollingMeanMT(bMunging, mixin_pab, mixin_pnab):
    """ Example munging template, which implements a ffill using the generic
        pandas attribute based munging, and then a rolling mean."""
    def __init__(self, **kwargs):
        super(FFillRollingMeanMT, self).__init__()
        self._bld_pab_generic('ffill')
        self._bld_rolling_mean(**kwargs)

class RollingMeanFFillMT(bMunging, mixin_pab, mixin_pnab):
    """ Example munging template, which implements a rolling mean
        and a generic pandas attribute based munging step."""
    def __init__(self, **kwargs):
        super(RollingMeanFFillMT, self).__init__()
        self._bld_rolling_mean(**kwargs)
        self._bld_pab_generic('ffill')

class MultiExampleMT(bMunging, mixin_pnab, mixin_pab):
    """ Example munging template, which implements a pct_change
        and add, using two sets of kwargs"""
    def __init__(self, pct_change_kwargs, add_kwargs):
        super(MultiExampleMT, self).__init__()
        self._bld_pct_change(**pct_change_kwargs)
        self._bld_add(**add_kwargs)

class SimpleExampleMT(bMunging, mixin_pnab, mixin_pab):
    """ Example munging template, which has defaults to forward fill,
        and a minimum period argument of 5"""
    def __init__(self, periods, window):
        super(SimpleExampleMT, self).__init__()
        kwargs = {'periods': periods, 'fill_method': 'ffill'}
        self._bld_pct_change(**kwargs)
        kwargs = {'window': window, 'min_periods': 5}
        self._bld_rolling_mean(**kwargs)

#******************************************************************************
#
#  Source Templates
#
# Source Templates are any object which implements a property called
# as_dict.  The keywords and values of which are sufficient to pass to a
# a Feed constructor's source parameter, which then become FeedSource objects
# making up a source.
#
#******************************************************************************

from trump.templating.source_helpers import mixin_dbCon, mixin_dbIns


class DBapiST(bSource, mixin_dbCon, mixin_dbIns):
    """ implements the generic source information for a DBAPI 2.0 driver """
    def __init__(self, dsn=None, user=None, password=None, host=None,
                 database=None, sourcing_key=None):
        super(DBapiST, self).__init__()
        self._set_con_params(dsn, user, password, host, database, sourcing_key)


class SQLAlchemyST(bSource):
    """ implements the generic source information for a SQLAlchemy engine """
    def __init__(self, enginestr):
        raise NotImplementedError
        # super(SQLAlchemyST, self).__init__()
        # self.enginestr = enginestr
        # self.set_basic()


class PyDataDataReaderST(bSource):
    """ implements the pydata datareaders sources """
    def __init__(self, data_source, name, column='Close',
                 start='2000-01-01', end='now'):
        self.name = name
        self.start = start
        self.end = end
        self.data_source = data_source
        self.data_column = column

class WorldBankST(bSource):
    """ implements the pydata datareaders sources """
    def __init__(self, indicator, country, **kwargs):
        self.indicator = indicator
        self.country = country
        for arg, val in kwargs.iteritems():
            setattr(self, arg, val)
        
class PyDataCSVST(bSource):
    """ implements pandas.read_csv source """
    def __init__(self, filepath_or_buffer, data_column, **kwargs):
        self.filepath_or_buffer = filepath_or_buffer
        self.data_column = data_column
        
        for arg, val in kwargs.iteritems():
            setattr(self, arg, val)

#******************************************************************************
#
# Index Templates
#
# Index Templates are any object which implements sufficient information
# to fully define an IndexImplementer via it's name, case and associated 
# kwargs, vias three attributes called imp_name (string), case (string),
# kwargs (dict).
#
#******************************************************************************

class FFillIT(bIndex):
    def __init__(self, freq='B'):
        super(FFillIT, self).__init__()
        self.name = 'FFillIT'
        self.imp_name = 'DatetimeIndexImp'
        self.case = 'asfreq'
        self.kwargs = {'freq' : freq, 'method' : 'ffill'}

#******************************************************************************
#
# Validity Templates
#
# Validity Templates are any object which implements an attribute
# named 'validator', and optionally some additional arguments as arga, argb,
# argc, argd and arge.
#
#******************************************************************************

class FeedsMatchVT(bValidity):
    def __init__(self, feed_left=1, feed_right=2, lastx=10):
        super(FeedsMatchVT, self).__init__()
        self.validator = 'FeedsMatch'
        self.arga = feed_left
        self.argb = feed_right
        self.argc = lastx

class DateExistsVT(bValidity):
    def __init__(self, date='today'):
        super(DateExistsVT, self).__init__()
        self.validator = 'DateExists'
        self.arga = date

# *****************************************************************************
#
#  Feed Templates
#
# These objects need an tags, sourcing, munging and validity attribute
# defined.  They must be a list, dict, odict, and dict, respectively.
#
# *****************************************************************************


SKEY = 'explicit'


class DBapiFT(bFeed):
    """ Feed template for DBAPI 2.0, which collects up everything it needs
        via parameters about the connection and information."""
    def __init__(self, table=None, indexcol=None, datacol=None, dsn=None,
                 user=None, password=None, host=None, database=None,
                 sourcing_key=None):
        super(DBapiFT, self).__init__()
        self._set_stype()
        if sourcing_key:
            self._set_sourcing_key(sourcing_key)
        self.s = DBapiST(dsn, user, password, host, database, sourcing_key)
        if self.__class__.__name__ == 'DBapiFT':
            self.s._set_basic(table, indexcol, datacol)
        self._refresh_sourcing()
    def _refresh_sourcing(self):    
        self.sourcing = self.s.as_dict

    def _set_stype(self):
        self.meta['stype'] = 'DBAPI'

    def _set_sourcing_key(self, sourcing_key):
        """ sets a sourcing key, sourcing keys are used to pull information
        from configuring files.  They refer to "sections", in python's
        config parser."""
        self.meta['sourcing_key'] = sourcing_key


class ExplicitKeyColFT(DBapiFT):
    """ Feed template to implement a basic DBAPI Feed, using a keyed column"""
    def __init__(self, table, keycol, key, indexcol, datacol):
        super(ExplicitKeyColFT, self).__init__(sourcing_key=SKEY)
        self.s._set_keycol(table, keycol, key, indexcol, datacol)
        self.sourcing = self.s.as_dict

class ExplicitTwoKeyColFT(DBapiFT):
    """ Feed template to implement a basic DBAPI Feed, using a keyed column"""
    def __init__(self, table, keyacol, keya, keybcol, keyb, indexcol, datacol):
        super(ExplicitTwoKeyColFT, self).__init__(sourcing_key=SKEY)
        self.s._set_twokeycol(table, keyacol, keya, keybcol, keyb, indexcol, datacol)
        self.sourcing = self.s.as_dict

class ExplicitBasicFT(DBapiFT):
    """ Feed template to implement a basic DBAPI Feed, using explicit,
        table, index, and data columns. """
    def __init__(self, table, datacol, indexcol):
        super(ExplicitBasicFT, self).__init__(table=table,
                                              indexcol=indexcol,
                                              datacol=datacol,
                                              sourcing_key=SKEY)
        self.s._set_basic(table, indexcol, datacol)
        self.sourcing = self.s.as_dict


class ExplicitCommandFT(DBapiFT):
    """ Example use of pure SQL command """
    def __init__(self, command):
        super(ExplicitCommandFT, self).__init__(sourcing_key=SKEY)
        self.s._set_command(command)
        self.sourcing = self.s.as_dict


class EconFT(ExplicitKeyColFT):
    """ Example use of simplifying a keyed column table """
    def __init__(self, key):
        super(EconFT, self).__init__('econ', 'name', key, 'date', 'value')


class MyTableFT(ExplicitBasicFT):
    """ Example use of simplifying an explicity basic table """
    def __init__(self, table, datacol='value', indexcol='date'):
        super(MyTableFT, self).__init__(table, datacol, indexcol)


class SQLFT(ExplicitCommandFT):
    """ Just wrap inherit, for renaming purposes. """
    pass


class SQLAlchemyFT(bFeed):
    """ Example feed for SQLAlchemy.... """
    def __init__(self, enginestr, table):
        raise NotImplementedError
        # super(SQLAlchemyFT, self).__init__()
        # s = SQLAlchemyST(enginestr)
        # s.set_basic(table)
        # self.sourcing = s.as_dict

#******************************************************************************
#
#  Quandl
#
#******************************************************************************


class QuandlFT(bFeed):
    """ Feed tamplate for a Quandl data source """
    def __init__(self, dataset, **kwargs):
        super(QuandlFT, self).__init__()

        if 'authtoken' in kwargs:
            authtoken = kwargs['authtoken']
        else:
            authtoken = read_settings()['Quandl']['userone']['authtoken']
        tmp = {'dataset': dataset, 'authtoken': authtoken}
        tmp.update(kwargs)
        self.sourcing = tmp
        self._set_stype()

    def _set_stype(self):
        self.meta['stype'] = 'Quandl'


class QuandlSecureFT(QuandlFT):
    """
    Feed tamplate for a Quandl data source, authtoken left in config file.
    """
    def __init__(self, dataset, **kwargs):
        super(QuandlFT, self).__init__()
        tmp = {'dataset': dataset}
        tmp.update(kwargs)
        self.sourcing = tmp
        self._set_stype()
        self.meta['sourcing_key'] = 'userone'


#******************************************************************************
#
#   Google Finance
#
#******************************************************************************

class GoogleFinanceFT(bFeed):
    """ PyData reader feed, generalized for google finance. """
    def __init__(self, name, column='Close',
                 start='1995-01-01', end='now'):
        super(GoogleFinanceFT, self).__init__()
        source = PyDataDataReaderST('google', name, column=column,
                                    start=start, end=end)
        self.sourcing = source.as_dict
        self._set_stype(source)


#******************************************************************************
#
#   St. Louis FED (FRED)
#
#******************************************************************************

class StLouisFEDFT(bFeed):
    """ PyData reader feed, generalized for St Louis FED. """
    def __init__(self, name, column=None, start='1995-01-01', end='now'):
        super(StLouisFEDFT, self).__init__()
        acol = column or name
        source = PyDataDataReaderST('fred', name, acol,
                                    start=start, end=end)
        self.sourcing = source.as_dict
        self._set_stype(source)

#******************************************************************************
#
#   Yahoo Finance
#
#******************************************************************************


class YahooFinanceFT(bFeed):
    """ PyData reader feed, generalized for Yahoo Finance. """
    def __init__(self, name, column='Close', start='1995-01-01', end='now'):
        super(YahooFinanceFT, self).__init__()
        source = PyDataDataReaderST('yahoo', name, column=column,
                                    start=start, end=end)
        self.sourcing = source.as_dict
        self._set_stype(source)

#******************************************************************************
#
#   World Bank
#
#******************************************************************************


class WorldBankFT(bFeed):
    """ PyData reader feed, generalized for Yahoo Finance. """
    def __init__(self, indicator, country, **kwargs):
        super(WorldBankFT, self).__init__()
        source = WorldBankST(indicator, country, **kwargs)
        self.sourcing = source.as_dict
        print self.sourcing
        self._set_stype(source)
        
#******************************************************************************
#
#   File Readers
#
#******************************************************************************


class CSVFT(bFeed):
    """ Creates a feed from a CSV. """
    def __init__(self, filepath_or_buffer, data_column, **kwargs):
        super(CSVFT, self).__init__()
        source = PyDataCSVST(filepath_or_buffer, data_column,
                             **kwargs)
        self.sourcing = source.as_dict
        self.meta['stype'] = 'PyDataCSV'

if __name__ == '__main__':
    pass
