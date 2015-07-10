import inspect, sys
import datetime as dt
import pandas as pd

try:
    # the API for engarde/validada is in development, so this might change...
    # validity is a pretty fringe feature, at the moment
    # only do this
    from validada.core import ReturnSet
    from validada.slicers import iloc
    rs = ReturnSet('bool')
except:
    pass

#imported like this, cause otherwise the docs won't build.
series_equal = pd.util.testing.assert_series_equal
    
class ValidityCheck(object):
    def __init__(self, data, *args):
        self.data = data
        self.args = args
        
    @property
    def result(self):
        return True

class NoneMissing(ValidityCheck):
    def __init__(self, data, *args):
        self.data = data
        
        if len(args) > 1:
            self.ind = args[0]
            self.args = args[1:]
        elif len(args) == 1:
            self.ind = args[0]
            self.args = []
        else:
            self.ind = -25
            self.args = []
            
    @property
    def result(self):
        return rs.none_missing(self.data, iloc[self.ind:], *self.args)

class NoneMissingRecently(ValidityCheck):
    def __init__(self, data, *args):
        self.data = data
    @property
    def result(self):
        return rs.none_missing(self.data, iloc[-25:])
        
class HasDataPointOnDate(ValidityCheck):
    def __init__(self, data, *args):
        self.data = data
        if len(args) > 1:
            self.dt = args[0]
            self.args = args[1:]
        elif len(args) == 1:
            self.dt = args[0]
            self.args = []
        else:
            self.dt = 'today'
            self.args = []

        if isinstance(self.dt, (str, unicode)):
            if self.dt == 'today':
                self.dt = dt.date.today()
            elif self.dt == 'yesterday':
                self.dt = dt.date.today() - dt.timedelta(days=1)

    @property
    def result(self):
        return rs.has_in_index(self.data, obj=self.dt, try_ix=True, try_strftime=True, check_na=True)

class DateExists(HasDataPointOnDate):
    @property
    def result(self):
        return rs.has_in_index(self.data, obj=self.dt, try_ix=True, try_strftime=True, check_na=False)

class FeedsMatch(object):
    def __init__(self, data, left, right, lastn):
        self.data = data
        
        feed_left = "feed%03d" % (left)
        feed_right = "feed%03d" % (right)
        
        leftS = data[feed_left][-1*lastn:]
        rightS = data[feed_right][-1*lastn:]
        
        self.match = leftS.equals(rightS)
 
    @property
    def result(self):
        return self.match
        
def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

validitychecks = {cls[0]: cls[1] for cls in classes}
