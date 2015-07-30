import inspect
import sys

import pandas as pd

pdDatetimeIndex = pd.tseries.index.DatetimeIndex
pdInt64Index = pd.core.index.Int64Index
pdCoreIndex = pd.core.index.Index

import sqlalchemy as sqla

import datetime as dt

class IndexImplementer(object):

    """
    IndexImplementer is the base required to implement
    an index of a specific type.  The
    same instance is created at two points in
    the Trump dataflow:

    1. the datatable getting cached and
    2. the data being served.

    The IndexImplementer should be
    indempotent, and dataframe/series agnostic.
    """

    sqlatyp = sqla.Integer
    pytyp = int
    pindt = pd.Index

    def __init__(self, df_or_s, case, kwargs):
        """
        :param df_or_s:
            A pandas.Dataframe or pandas.Series, used
            with caution as to the point in time of use.
        :param case: str
            This should match a case used to switch
            the logic created in each subclass of IndexImplementer

        :param kwargs: dict
        """
        self.data = df_or_s
        self.case = case
        self.kwargs = kwargs

#    def final_series(self):
#        """
#        Should only be called when serving the final
#        result.  In this case, at instantiation, df_or_s
#        should be a pandas.Series,
#
#        :return: pandas.Series
#        """
#
#        # When Trump is serving up the final data,
#        # it should be impossible that df_or_s isn't
#        # a Series.  If, for any reason that it isn't,
#        # it should be converted into one here.
#
#        return self.data
#
#    def final_dataframe(self):
#        """
#        Should only be called when caching the feeds.
#        In this case, at instantiation, df_or_s
#        should be a pandas.Dataframe,
#
#        :return: pd.Dataframe
#        """
#
#        # if it's possible that df_or_s isn't a
#        # pandas.Dataframe, at the time of instatiation of the
#        # IndexImplementer, than it should be converted
#        # into one here.
#
#        if isinstance(self.data, pd.Series):
#            return self.data.to_frame()
#        else:
#            return self.data
#            
#    def raw_data(self):
#        """
#        returns the raw dataframe or series, after
#        it's been cleaned up by the index implementer.
#        
#        Should only be used via validation
#
#        :return: pd.Dataframe
#        """
#        return self.data      
class DateIndexImp(IndexImplementer):
    sqlatyp = sqla.Date
    pytyp = dt.date
    pindt = pd.Index
    def __init__(self, dfors, case, kwargs):
        raise NotImplemented()
        
class DatetimeIndexImp(IndexImplementer):
    """
    Implements a pandas DatetimeIndex

    Cases include:

    * **asis** - Cache timestamps to the database and drop
      any intelligence associated with the index, such as frequency.
      serve a Series with a DatetimeIndex, without frequency.

      If the index consists of 4-digit integers, it will
      be treated as the year, in a date which is of the form
      YYYY-12-31.

    * **asfreq** - Apply 'asfreq' logic prior to cache, and
      apply the same logic when serving.

    * **date_range** - Create a new index, using pandas date_range(), at
      time of cache...  NotImplemented yet.

    * **guess** - NotImplemented yet.
      Attempt to guess the frequency at time of cache,
      and time of serve.

    * **guess_post** - NotImplemented yet.
      Attempt to guess the frequency at time of serve,
      but store the cache unsaved.

    In the event that case hasn't implemented the logic
    to handle a specific datatype, a rudimentary
    attempt to convert it to a DatetimeIndex is applied
    by inspecting the start and end, with the kwargs. passed
    pandas.DatetimeIndex constructor.

    """
    sqlatyp = sqla.DateTime
    pytyp = dt.datetime
    pindt = pd.DatetimeIndex

    def __init__(self, case, **kwargs):
                
        self.case = case
        self.k = kwargs
    
    def orfs_ind_from_str(self, userinput):
        ui = {}
        exec("ui = " + userinput)
        obj = self.pytyp(**ui)
        return obj
    def create_empty(self):
        return self.pindt([])
    def for_loc(self, obj):
        return obj
    def apply_orfs(self, df, obj, value, orfs='OVERRIDE'):
        # TODO handle extending the index, if appropriate, here.
        if 'OVERRIDE':
            col = 'override_feed000'
        elif 'FAILSAFE':
            col = 'failsafe_feed999'
        df.loc[obj,col] = value
        return df  
    def _common_passthrough(self, obj):
        try:
            return getattr(self, '_' + self.case)(obj)
        except AttributeError:
            self._notimp_error(self)
    def _notimp_error(self):
        msg = "Indexing case '{}' unsupported for Index Implementer {}"
        msg = msg.format(self.case, self.__name__)
        raise NotImplementedError(msg)        
    def _notimpobj_error(self, obj):
        msg = "Object of type '{}' unsupported for Index Implementer {}, case {}"
        msg = msg.format(type(obj), self.__name__, self.case)
        raise TypeError(msg)

    def process_post_db(self, dat, ind):
        df = pd.DataFrame(data=dat, index=ind)
        return self._common_passthrough(df)
    def process_post_source(self, s):
        return self._common_passthrough(s)
    def process_post_concat(self, df):
        return self._common_passthrough(df)
    def _asis(self, obj):
        if isinstance(obj.index, pdDatetimeIndex):
            return obj
        elif isinstance(obj.index, pdInt64Index):
            if all(len(str(i)) == 4 for i in obj.index):
                #safe to assume we meant years...
                newind = [dt.date(y, 12, 31) for y in obj.index]
                obj.index = newind
                obj.index = obj.index.to_datetime()
                return obj
            self._notimpobj_error(obj)
        elif isinstance(obj.index, pdCoreIndex):
            if isinstance(obj.index[0], dt.date):
                newind = pdDatetimeIndex(obj.index)
                obj.index = newind
                return obj
            self._notimpobj_error(obj)
        else:
            return self.default(**self.k)
        
    def _asfreq(self, obj):
        if isinstance(obj.index, pdDatetimeIndex):
            obj = obj.asfreq(**self.k)
        elif isinstance(obj.index, pdInt64Index):
            if all(len(str(i)) == 4 for i in obj.index):
                #safe to assume we meant years...
                newind = [dt.date(y, 12, 31) for y in obj.index]
                obj.index = newind
                obj.index = obj.index.to_datetime()
                obj = obj.asfreq(**self.k)
                return obj
            self._notimpobj_error(obj)
        elif isinstance(obj.index[0], (str, unicode)):
            newind = pd.DatetimeIndex(obj.index)
            obj.index = newind
            obj = obj.asfreq(**self.k)
            return obj
        else:
            self.default(**self.k)
            
    @staticmethod
    def _default(obj, **kwargs):
        start = pd.to_datetime(obj.index[0])
        end = pd.to_datetime(obj.index[-1])
        newind = pdDatetimeIndex(start=start, end=end, **kwargs)
        obj = obj.reindex(newind)
        return obj


class PeriodIndexImp(IndexImplementer):
    """
    Implements a pandas PeriodIndex

    NotImplemented, yet.
    """
    sqlatyp = sqla.DateTime
    pytyp = pd.Period
    pindt = pd.PeriodIndex

    def __init__(self, dfors, case, kwargs):
        raise NotImplementedError()


class IntIndexImp(IndexImplementer):
    """
    Implements a pandas Int64Index.

    Cases include:

    * **asis** - attempts to pass the index through,
      without applying any logic.  Use this, if the index
      is already integers, or unique and integer-like.

    * **force** - Not Implemented Yet...
      Will force floats into integers, dropping rows
      based on kwargs...

    In the event that a case hasn't implemented the logic
    to handle a specific data type, the index will be dropped via
    the .reset_index() method.

    """

    sqlatyp = sqla.Integer
    pytyp = int
    pindt = pd.Index

    def __init__(self, dfors, case, kwargs):
        self.data = dfors
        if case == 'asis':
            if isinstance(self.data.index, pdInt64Index):
                pass
            else:
                self.data = self.data.reset_index(drop=True)
        elif case == 'force':
            raise NotImplementedError("force not implemented, yet.")
        else:
            raise Exception("Indexing case '{}' unsupported".format(case))

class StrIndexImp(IndexImplementer):
    """
    Implements a pandas Index consisting of string objects.

    NotImplemented, yet.
    """
    sqlatyp = sqla.String
    pytyp = str
    pindt = pd.Index

    def __init__(self, dfors, case, kwargs):
        raise NotImplementedError()


def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

indexingtypes = {cls[0]: cls[1] for cls in classes}
