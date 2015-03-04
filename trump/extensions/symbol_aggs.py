# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 17:12:03 2015

@author: Jeffrey
"""
from types import FunctionType

#TODO : Decide if all of these functions should have the same argument signature

#Design Options:
#1. Run only one of these per symbol, enable infinite arguments -> **params needed
#2. Run one from each function group, what to do with params for each?
#3. Run as many in static order, enable infinite arguments -> **params needed
#4. Run an ordered list of them, set in the symbol's params
# To start, build #1.  There rest get more confusing.

def apply_row_funcs():
    def priority_fill(adf):
        """
        Looks at each row, and chooses the value from the highest priority 
        (lowest #) feed, one row at a time.
        """
        #TODO : Take out the override columns.  That behavious should be
        #       Extension agnostic.
        adf.index = [int(x[-3:]) for x in adf.index]
        adf = adf.sort_index()
        for n in adf.values:
            if n is not None:
                return n

    def mean_fill(adf):
        """
        Looks at each row, and calculates the mean
        """
        adf.index = [int(x[-3:]) for x in adf.index]
        return adf.values.mean

    def mode_fill(adf):
        """
        Looks at each row, and chooses the mode
        """
        adf.index = [int(x[-3:]) for x in adf.index]
        return adf.values.mode
    
    return {k.upper() : v for k,v in locals().items() if isinstance(v,FunctionType)}

def choose_col_funcs():
    def most_populated(adf):
        """
        Looks at each column, and counts the column the most recently updated
        """
        raise NotImplementedError
    def most_recent(adf):
        """
        Looks at each column, and chooses the feed with the most recent data
        """
        raise NotImplementedError

    return {k.upper() : v for k,v in locals().items() if isinstance(v,FunctionType)}

apply_row = apply_row_funcs()
choose_col = choose_col_funcs()

