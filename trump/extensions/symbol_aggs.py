# -*- coding: utf-8 -*-
###############################################################################
#
# PyLint tests that will never be applied for this file.
#
# Unused variables, these functions are organized so that they can be called
#                    from a string at runtime, from it's name being stored
#                    in an SQLAlchemy object attribute.
# pylint: disable-msg=W0612

###############################################################################
#
# PyLint tests that will be eventually fixed.
#
# Unused argument, the functionality, once it's implemented, will use
#                  the argument.
# pylint: disable-msg=W0613

"""
This module creates the functions that get used in symbol aggregation

There are row-based, and column-based, function builders, just to stay
organized.
"""
from types import FunctionType


def apply_row_funcs():
    """
    Builds a dictionary of row-based logic to be applied by
    Trump's aggregation step.

    All these functions, should take in a dataframe of multiple columns,
    and return a DataFrame with a single column, or a Series.
    """
    def priority_fill(adf):
        """
        Looks at each row, and chooses the value from the highest priority
        (lowest #) feed, one row at a time.
        """
        adf.index = [int(x[-3:]) for x in adf.index]
        adf = adf.sort_index()
        for n in adf.values:
            if n is not None:
                return n

    def mean_fill(adf):
        """ Looks at each row, and calculates the mean """
        adf.index = [int(x[-3:]) for x in adf.index]
        return adf.values.mean

    def mode_fill(adf):
        """ Looks at each row, and chooses the mode """
        adf.index = [int(x[-3:]) for x in adf.index]
        return adf.values.mode

    lcls = locals().items()
    return {k.upper(): v for k, v in lcls  if isinstance(v, FunctionType)}


def choose_col_funcs():
    """
    Builds a dictionary of column-based logic to be applied by
    Trump's aggregation step.

    All these functions, should take in a dataframe of multiple columns,
    and return a DataFrame with a single column, or a Series.
    """
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

    lcls = locals().items()
    return {k.upper(): v for k, v in lcls if isinstance(v, FunctionType)}

apply_row = apply_row_funcs()
choose_col = choose_col_funcs()
