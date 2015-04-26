import inspect
import sys

import pandas as pd
import datetime as dt
from sqlalchemy import DateTime, Integer, String, Float

class SkipDataDef(object):
    """
    The SkipDataDef object implements a float column, but makes an assumption
    that the data is already floats (or float-like), so it can skip any
    check and conversion. It's just faster.
    """
    sqlatyp = Float
    astyp = float

    def __init__(self, data):
        self.data = data
 
    @property
    def converted(self):
        return self.data

class ConvertedDataDef(object):
    """
    Implements a basic functionality for a DataDef object.
    
    The defaults, are floats.
    """
    sqlatyp = Float
    pythontyp = float

    def __init__(self, data):
        self.data = data
        
    @property
    def converted(self):       
        return self.data.astype(self.pythontyp)

class IntDataDef(ConvertedDataDef):
    """Implements a basic integer data definition."""
    sqlatyp = Integer
    pythontyp = int

class FloatDataDef(ConvertedDataDef):
    """Implements a basic float data definition."""
    # redefined, just to avoid confusion.  Floats are used by 
    # default in ConvertedDataDef
    sqlatyp = Float 
    pythontyp = float
      
class StrDataDef(ConvertedDataDef):
    """Implements a basic string data definition."""
    sqlatyp = String
    pythontyp = str

    def __init__(self, data):
        self.data = data
        
        #raise Warning("""Using this DataDef, on a feed with NaN, will convert
        #the NaN to a string.  The Aggregation functions will treat this as a 
        #value.""")

class DateTimeDataDef(ConvertedDataDef):
    """Implements a basic string data definition."""
    sqlatyp = DateTime
    pythontyp = dt.datetime
       
    @property
    def converted(self):
        return pd.to_datetime(self.data)
        
def _pred(aclass):
    """
    :param aclass
    :return: boolean
    """
    isaclass = inspect.isclass(aclass)
    return isaclass and aclass.__module__ == _pred.__module__

classes = inspect.getmembers(sys.modules[__name__], _pred)

datadefs = {cls[0]: cls[1] for cls in classes}
