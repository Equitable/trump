import inspect
import sys
import datetime as dt
import pandas as pd

#imported like this, cause otherwise the docs won't build.
series_equal = pd.util.testing.assert_series_equal

class ValidityCheck(object):
    def __init__(self, data, *args):
        self.data = data
        self.args = args
        
    @property
    def result(self):
        return True

class FeedsMatch(object):
    def __init__(self, data, left, right, lastn):
        self.data = data
        
        feed_left = "feed%03d" % (left)
        feed_right = "feed%03d" % (right)
        
        self.match = False
        
        series_equal(data[feed_left][-1*lastn:],
                     data[feed_right][-1*lastn:],
                     check_names=False)
        self.match = True
 
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
