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
import pandas as pd

nan = pd.np.nan

def sorted_feed_cols(df):
    """
    takes a dataframe's columns that would be of the form:
    ['feed003', 'failsafe_feed999', 'override_feed000', 'feed001', 'feed002']
    and returns:
    ['override_feed000', 'feed001', 'feed002', 'feed003', 'failsafe_feed999']
    """
    cols = df.columns
    ind = [int(c.split("feed")[1]) for c in cols]
    cols = zip(ind,cols)
    cols.sort()
    cols = [c[1] for c in cols]
    return cols

def _row_wise_priority(adf):
    adf = adf.dropna()
    if len(adf) > 0:
        return adf.values[0]
    else:
        return nan

class ApplyRow(object):
    """
    Mixer used to identify row-based logic methods for
    Trump's Feed aggregation step.

    All these functions, should take in a dataframe of multiple columns,
    and return a DataFrame with a single column, or a Series.
    """

    @staticmethod
    def priority_fill(adf):
        """
        Looks at each row, and chooses the value from the highest priority
        (lowest #) feed, one row at a time.
        """

        # the logic to apply overrides, values from certain feeds,
        # or the failsafes, is needed for high-level functions
        # in this same file.

        # so "priority_fill" just wraps this, for organization
        # purposes.
        return _row_wise_priority(adf)
    
    @staticmethod
    def mean_fill(adf):
        """ Looks at each row, and calculates the mean. Honours
        the Trump override/failsafe logic. """
        ordpt = adf.values[0]
        if not pd.isnull(ordpt):
            return ordpt

        fdmn = adf.iloc[1:-1].mean()
        if not pd.isnull(fdmn):
            return fdmn

        flspt = adf.values[-1]
        if not pd.isnull(flspt):
            return flspt

        return nan
    
    @staticmethod
    def median_fill(adf):
        """ Looks at each row, and chooses the median. Honours
        the Trump override/failsafe logic. """
        ordpt = adf.values[0]
        if not pd.isnull(ordpt):
            return ordpt

        fdmn = adf.iloc[1:-1].median()
        if not pd.isnull(fdmn):
            return fdmn

        flspt = adf.values[-1]
        if not pd.isnull(flspt):
            return flspt

        return nan

    @staticmethod
    def custom(adf):
        """
        A custom Apply-Row Aggregator can be defined,
        as any function which accepts a Series, and returns
        any number-like object, which will get
        assigned to the Dataframe's 'final' column in
        using the pandas .apply, function.
        """
        return [0] * len(adf)


class ChooseCol(object):
    """
    Builds a dictionary of column-based logic to be applied by
    Trump's aggregation step.

    All these functions, should take in a dataframe of multiple columns,
    and return a DataFrame with a single column, or a Series.
    """
    @staticmethod
    def most_populated(adf):
        """
        Looks at each column, using the one with the most values
        Honours the Trump override/failsafe logic. """

        # just look at the feeds, ignore overrides and failsafes:
        feeds_only = adf[adf.columns[1:-1]]

        # find the most populated feed
        cnt_df = feeds_only.count()
        cnt = cnt_df.max()
        selected_feeds = cnt_df[cnt_df == cnt]

        # if there aren't any feeds, the first feed will work...
        if len(selected_feeds) == 0:
            pre_final = adf['feed001'] # if they are all empty
                                  # they should all be
                                  # equally empty
        else:
            #if there's one or more, take the highest priority one
            pre_final = adf[selected_feeds.index[0]]


        # create the final, applying the override and failsafe logic...
        final_df = pd.concat([adf.override_feed000,
                              pre_final,
                              adf.failsafe_feed999], axis=1)
        final_df = final_df.apply(_row_wise_priority, axis=1)
        return final_df

    @staticmethod
    def most_recent(adf):
        """
        Looks at each column, and chooses the feed with the most recent data
        point. Honours the Trump override/failsafe logic. """
        # just look at the feeds, ignore overrides and failsafes:
        feeds_only = adf[adf.columns[1:-1]]

        # find the feeds with the most recent data...
        feeds_with_data = feeds_only.dropna(how='all')
        selected_feeds = feeds_with_data.T.dropna().index

        # if there aren't any feeds, the first feed will work...
        if len(selected_feeds) == 0:
            pre_final = adf['feed001'] # if there all empyty
                                  # they should all be
                                  # equally empty
        else:
            #if there's one or more, take the highest priority one
            pre_final = adf[selected_feeds[0]]


        # create the final, applying the override and failsafe logic...
        final_df = pd.concat([adf.override_feed000,
                              pre_final,
                              adf.failsafe_feed999], axis=1)
        final_df = final_df.apply(_row_wise_priority, axis=1)
        return final_df

    @staticmethod
    def custom(adf):
        """
        A custom Choose-Column Aggregator can be defined,
        as any function which accepts a dataframe, and returns
        any Series-like object, which will get
        assigned to the Dataframe's 'final' column.
        """
        return [0] * len(adf)

class FeedAggregator(ApplyRow, ChooseCol):
    def __init__(self,method):
        try:
            self.meth = getattr(self, method)
        except:
            raise "{} is not an arggregator method".format(method)
        self.methname = method
    def aggregate(self,df):
        if self.methname in ApplyRow.__dict__:
            return df.apply(self.meth, axis=1)
        elif self.methname in ChooseCol.__dict__:
            return self.meth(df)
        else:
            NotImplemented("This code path could be an ugly implementation, " + \
                           "of a default?")

if __name__ == '__main__':

    def make_fake_feed_data(l=10):
        dr = pd.date_range(start='2015-01-10', periods=l, freq='D')
        data = pd.np.random.rand(l)
        return pd.Series(data,dr)

    ors = make_fake_feed_data(1).shift(1,freq='D')
    s1 = make_fake_feed_data(10)
    s2 = make_fake_feed_data(5)
    s3 = make_fake_feed_data(7)
    fls = make_fake_feed_data(1).shift(8,freq='D')

    s1.iloc[6] = pd.np.nan
    s1.iloc[8] = pd.np.nan

    cols = ['override_'] + [''] * 3
    cols = [c + "feed{0:03d}".format(i) for i, c in enumerate(cols)]
    cols = cols + ['failsafe_feed999']

    df = pd.concat([ors, s1, s2, s3, fls], axis=1)
    df.columns = cols
    df['final'] = FeedAggregator('most_populated').aggregate(df)

    print df

    #assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
    #assert df['final'].iloc[-1] == df['feed001'].iloc[-1]
    #assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
    #assert df['final'].iloc[-4] == df['feed003'].iloc[-4]


