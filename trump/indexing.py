import inspect
import sys

import pandas as pd

pdDatetimeIndex = pd.tseries.index.DatetimeIndex
pdInt64Index = pd.core.index.Int64Index
pdCoreIndex = pd.core.index.Index

from sqlalchemy import DateTime, Integer, String

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

    sqlatyp = Integer

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

    def final_series(self):
        """
        Should only be called when serving the final
        result.  In this case, at instantiation, df_or_s
        should be a pandas.Series,

        :return: pandas.Series
        """

        # When Trump is serving up the final data,
        # it should be impossible that df_or_s isn't
        # a Series.  If, for any reason that it isn't,
        # it should be converted into one here.

        return self.data

    def final_dataframe(self):
        """
        Should only be called when caching the feeds.
        In this case, at instantiation, df_or_s
        should be a pandas.Dataframe,

        :return: pd.Dataframe
        """

        # if it's possible that df_or_s isn't a
        # pandas.Dataframe, at the time of instatiation of the
        # IndexImplementer, than it should be converted
        # into one here.

        if isinstance(self.data, pd.Series):
            return self.data.to_frame()
        else:
            return self.data
            
    def raw_data(self):
        """
        returns the raw dataframe or series, after
        it's been cleaned up by the index implementer.
        
        Should only be used via validation

        :return: pd.Dataframe
        """
        return self.data      
        
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
    sqlatyp = DateTime

    def __init__(self, dfors, case, kwargs):
        
        
        self.data = dfors
	  
        if case == 'asis':
            if isinstance(self.data.index, pdDatetimeIndex):
                pass
            elif isinstance(self.data.index, pdInt64Index):
                if all(len(str(i)) == 4 for i in self.data.index):
                    #safe to assume we meant years...
                    newind = [dt.date(y, 12, 31) for y in self.data.index]
                    self.data.index = newind
                    self.data.index = self.data.index.to_datetime()
            elif isinstance(self.data.index, pdCoreIndex):
                if isinstance(self.data.index[0], dt.date):
                    newind = pdDatetimeIndex(self.data.index)
                    self.data.index = newind
            else:
                self.default(**kwargs)

        elif case == 'asfreq':
            if isinstance(self.data.index, pdDatetimeIndex):
                self.data = self.data.asfreq(**kwargs)
            elif isinstance(self.data.index, pdInt64Index):
                if all(len(str(i)) == 4 for i in self.data.index):
                    #safe to assume we meant years...
                    newind = [dt.date(y, 12, 31) for y in self.data.index]
                    self.data.index = newind
                    self.data.index = self.data.index.to_datetime()
                    self.data = self.data.asfreq(**kwargs)
            elif isinstance(self.data.index[0], (str, unicode)):
                newind = pd.DatetimeIndex(self.data.index)
                self.data.index = newind
                self.data = self.data.asfreq(**kwargs)
            else:
                self.default(**kwargs)
        elif case == 'guess':
            raise NotImplementedError()
        elif case == 'guess_post':
            raise NotImplementedError()
        else:
            raise Exception("Indexing case '{}' unsupported".format(case))

    def default(self, **kwargs):
        start = pd.to_datetime(self.data.index[0])
        end = pd.to_datetime(self.data.index[-1])
        newind = pdDatetimeIndex(start=start, end=end, **kwargs)
        self.data = self.data.reindex(newind)


class PeriodIndexImp(IndexImplementer):
    """
    Implements a pandas PeriodIndex

    NotImplemented, yet.
    """
    sqlatyp = DateTime

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

    sqlatyp = Integer

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
    sqlatyp = String

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
