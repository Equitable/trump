import inspect
import sys

import pandas as pd
from pandas.tseries.index import DatetimeIndex as pdDatetimeIndex

from sqlalchemy import DateTime, Integer, String


class IndexImplementor(object):

    """ IndexImplementors are the final step applied to data prior
        to a) the datatable getting cached and b) the data being served.

        The goal is that the transformations applied should be
        indempotent, and dataframe/series agnostic.

        They need to be able to handle
    """
    sqlatyp = Integer

    def __init__(self, df_or_s, case, kwargs):
        self.data = df_or_s

    def final_series(self):
        return self.data

    def final_dataframe(self):
        return self.data


class DatetimeIndex(IndexImplementor):
    sqlatyp = DateTime

    def __init__(self, dfors, case, kwargs):
        self.data = dfors

        if case == 'asis':
            if isinstance(self.data.index, pdDatetimeIndex):
                pass
            else:
                self.default(kwargs)

        elif case == 'asfreq':
            if isinstance(self.data.index, pdDatetimeIndex):
                self.data = self.data.asfreq(**kwargs)
            else:
                self.default(kwargs)

        elif case == 'freqchng':
            if isinstance(self.data.index, pdDatetimeIndex):
                self.data = self.data.asfreq(**kwargs)
            else:
                self.default(kwargs)

        else:
            raise Exception("Indexing case '{}' unsupported".format(case))

    def default(self, kwargs):
        start = pd.to_datetime(self.data.index[0])
        end = pd.to_datetime(self.data.index[-1])
        newind = pdDatetimeIndex(start=start, end=end, **kwargs)
        self.data = self.data.reindex(newind)


class PeriodIndex(IndexImplementor):
    sqlatyp = DateTime

    def __init__(self, df_or_s, case, kwargs):
        raise NotImplementedError()


class IntIndex(IndexImplementor):
    sqlatyp = Integer

    def __init__(self, df_or_s, case, kwargs):
        raise NotImplementedError()


class StrIndex(IndexImplementor):
    sqlatyp = String

    def __init__(self, df_or_s, case, kwargs):
        raise NotImplementedError()


def pred(c):
    return inspect.isclass(c) and c.__module__ == pred.__module__

classes = inspect.getmembers(sys.modules[__name__], pred)

indexingtypes = {cls[0]: cls[1] for cls in classes}
tosqla = {cls[0]: cls[1].sqlatyp for cls in classes}
