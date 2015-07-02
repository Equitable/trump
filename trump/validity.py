import inspect
import sys
import datetime as dt
import pandas as pd

try:
    # the API for engard is in development, so this might change...
    # validity is a pretty fringe feature, at the moment
    from engard import ReturnSet, iloc
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

def engarde_validity_check_maker(name, slc=None, slcd=None):
    class aValCheck(ValidityCheck):
        def __init__(self, data, *args):
            self.data = data
            func = getattr(rs, name)
            
            args = list(args)
            
            if slc and slcd:
                self.valid = func(self.data['final'], slc, slcd, *self.args)
            elif slc:
                self.valid = func(self.data['final'], slc, *self.args)
            elif slcd:
                self.valid = func(self.data['final'], slice(None), slcd, *self.args)
            else:
                self.valid = func(self.data['final'], *self.args)
        @property
        def result(self):
            return self.valid

NoneMissing = engarde_validity_check_maker('none_missing')
#NoneMissingRecently = engarde_validity_check_maker('none_missing', iloc[-3:])
     
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

class DateExists(object):
    def __init__(self, data, date='today'):
        self.data = data
        
        if isinstance(date, (str, unicode)):
            if date == 'today':
                cur_date = dt.date.today()
            elif date == 'yesterday':
                cur_date = dt.date.today() - dt.timedelta(days=1)
            else:
                raise Exception("{} is not convertible to a date".format(date))
        else:
            cur_date = date
        
        self.today_exists = cur_date in self.data.index
        
    @property
    def result(self):
        return self.today_exists
        
def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

validitychecks = {cls[0]: cls[1] for cls in classes}
