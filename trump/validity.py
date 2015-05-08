import inspect
import sys

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

class FeedMatch(object):
    def __init__(self, data, left, right, lastn):
        self.data = data

        feed_left = "feed%03d" % (left)
        feed_right = "feed%03d" % (right)
        
        self.match = series_equal(data[feed_left][-1*lastn:],
                                  data[feed_right][-1*lastn:])
        
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
