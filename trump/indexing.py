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

    def __init__(self, case, **kwargs):
        """
        :param case: str
            This should match a case used to switch
            the logic created in each subclass of IndexImplementer
        :param kwargs: dict
        """
                
        self.case = case
        self.k = kwargs
    def orfs_ind_from_str(self, userinput):
        ui = {}
        exec("ui = " + userinput)
        obj = self.pytyp(**ui)
        return obj
    def create_empty(self):
        return self.pindt([])
    def build_ordf(self, orind, orval, colname):
        ordf = pd.DataFrame(index=orind, data=orval, columns=[colname])
        return self._common_passthrough(ordf)
    def _common_passthrough(self, obj):
        try:
            if len(obj.index) > 0:
                return getattr(self, '_' + self.case)(obj)
            else:
                obj.index = self.create_empty()
                return obj
        except AttributeError:
            self._notimp_error()
    def _notimp_error(self):
        msg = "Indexing case '{}' unsupported for Index Implementer {}"
        msg = msg.format(self.case, self.__class__.__name__)
        raise NotImplementedError(msg)        
    def _notimpobj_error(self, obj):
        msg = "Object of type '{}' unsupported for Index Implementer {}, case {}"
        msg = msg.format(type(obj), self.__class__.__name__, self.case)
        raise TypeError(msg)

    def process_post_db(self, df):
        return self._common_passthrough(df)
    def process_post_feed_cache(self, s):
        return self._common_passthrough(s)
    def process_post_orfs(self, df):
        return self._common_passthrough(df)
   
class DateIndexImp(IndexImplementer):
    sqlatyp = sqla.Date
    pytyp = dt.date
    pindt = pd.Index
    def __init__(self, case, **kwargs):
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
            return self._default(obj, **self.k)
        
    def _asfreq(self, obj):
        if isinstance(obj.index, pdDatetimeIndex):
            obj = obj.asfreq(**self.k)
            return obj
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
            return self._default(obj, **self.k)
            
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
    def __init__(self, case, **kwargs):
        raise NotImplementedError()

class IntIndexImp(IndexImplementer):
    """
    Implements a pandas Int64Index.

    Cases include:

    * **asis** - attempts to pass the index through,
      without applying any logic.  Use this, if the index
      is already integers, or unique and integer-like.

    * **drop** - will drop the pandas index, to reset it.

    """

    sqlatyp = sqla.Integer
    pytyp = int
    pindt = pd.Index

    def _asis(self, obj):
        if isinstance(obj.index, pdInt64Index):
            return obj
        self._notimp_error()
    def _drop(self, obj):
        obj = obj.reset_index(drop=True)
        return obj
            
class StrIndexImp(IndexImplementer):
    """
    Implements a pandas Index consisting of string objects.

    Only method, is "asis"
    """
    sqlatyp = sqla.String
    pytyp = str
    pindt = pd.Index

    def _asis(self, obj):
        if isinstance(obj.index, pdCoreIndex):
            return obj
        self._notimp_error()


def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

indexingtypes = {cls[0]: cls[1] for cls in classes}