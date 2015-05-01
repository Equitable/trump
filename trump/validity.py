import inspect
import sys

import pandas as pd

class ValidityCheck(object):
    def __init__(self, data, *args):
        self.data = data
        self.args = args
        
    @property
    def result(self):
        return True

class FeedMatch(object):
    def __init__(self, data, *args):
        self.data = data
        self.args = args
        
    @property
    def result(self):
        return True

def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

validitychecks = {cls[0]: cls[1] for cls in classes}
