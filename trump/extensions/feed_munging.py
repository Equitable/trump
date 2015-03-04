# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 17:12:03 2015

@author: Jeffrey
"""
from types import FunctionType

#TODO: Kick the tires harder on this file harder.

#Split them via...
#   ordered (requires API change) & unordered?
#   num of params?
#   One single list -> purely explicit, don't enable parameters at all?
#   One single list -> purely explicit, enable just a single switch parameter?
#   Constructive? 
#   Incorporate all pandas functions somehow?

from arghack import unpacker    
            
def str_to_num(n):
    if isinstance(n,str) or isinstance(n,unicode) :
        if '.' in n:
            return float(n)
        else:
            return int(n)
    return n

# This file creates a dictionary of less-than-pythonic functions.  
# The dictionary enables us to not need to import these functions
# in other parts of Trump, it enables us to intelligently switch how to
# handle arguments passed during symbol adding, and it makes it so they
# can be called at runtime based on database entries matching their exact
# name, even if they are changed.  In short, type them once below, and once
# where they are used, and nowhere else.  

# Notice that each function built, is wrapped using unpacker.  Doing this,
# as opposed to a decorator, allows for the dictionary to be built properly.

# There can only be two styles of arguments used in these functions.  Either 
# explicit (no use of **kwargs), or 100% key-word based.  
# The argument name 'adf' is special and reserved; all functions must have
# an argument named 'adf', in the first position, even if it's unused.
# No arguments are allowed to be of the form arg####, those are reserved
# by TRUMP. So, if you need **kwargs, as well as other explicit arguments,
# simply raise an exception if you don't get them. Otherwise, don't use **kwargs.

def munging_method_builder():
    def multiply_const(adf,n):
        return adf * str_to_num(n)

    def add_const(adf,n):
        return adf + str_to_num(n)

    def exp_const(adf,n):       
        return adf ** str_to_num(n)

    def crop_dates(adf,start,end): 
        return adf[start:end]

    def fillna(adf,**kwargs):
        return adf.fillna(**kwargs)
        
    return {k : unpacker(v,'adf') for k,v in locals().items() if isinstance(v,FunctionType)}

munging_methods = munging_method_builder()

if __name__ == '__main__':
    import pandas as pd

    test_df = pd.Series([1,2.1,3,4,5])

    args = {u'arg0': u'3'}
    print munging_methods['MULTIPLY_CONST'](test_df,**args)