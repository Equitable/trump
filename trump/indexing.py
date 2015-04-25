import inspect
import sys

import pandas as pd

pdDatetimeIndex = pd.tseries.index.DatetimeIndex

from sqlalchemy import DateTime, Integer, String


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


class DatetimeIndexImp(IndexImplementer):
    """
    Implements a pandas DatetimeIndex

    Cases include:

    * **asis** - Cache timestamps to the database and drop
      any intelligence associated with the index, such as frequency.
      serve a Series with a DatetimeIndex, without frequency.

    * **asfreq** - Apply 'asfreq' logic prior to cache, and
      apply the same logic when serving.

    * **date_range** - Create a new index, using pandas date_range(), at
      time of cache...  NotImplemented yet.

    * **guess** - Attempt to guess the frequency at time of cache,
      and time of serve. NotImplemented yet.

    * **guess_post** - Attempt to guess the frequency at time of serve,
      but store the cache unsaved. NotImplemented yet.

    If a non-DatetimeIndex is passed, a rudimentary
    attempt to convert it to a DatetimeIndex is applied
    by inspecting the start and end, then using any saved kwargs.
    """
    sqlatyp = DateTime

    def __init__(self, dfors, case, kwargs):
        self.data = dfors
	
        if case == 'asis':
            if isinstance(self.data.index, pdDatetimeIndex):
                pass
            else:
                print type(self.data.index)
                self.default(**kwargs)

        elif case == 'asfreq':
            if isinstance(self.data.index, pdDatetimeIndex):
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

    def __init__(self, df_or_s, case, kwargs):
        raise NotImplementedError()


class IntIndexImp(IndexImplementer):
    """
    Implements a pandas Int64Index

    NotImplemented, yet.
    """
    sqlatyp = Integer

    def __init__(self, df_or_s, case, kwargs):
        raise NotImplementedError()


class StrIndexImp(IndexImplementer):
    """
    Implements a pandas Index consisting of string objects.

    NotImplemented, yet.
    """
    sqlatyp = String

    def __init__(self, df_or_s, case, kwargs):
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
tosqla = {cls[0]: cls[1].sqlatyp for cls in classes}
