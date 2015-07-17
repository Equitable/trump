from trump.aggregation.symbol_aggs import FeedAggregator

import pandas as pd

def make_fake_feed_data(l=10):
    dr = pd.date_range(start='2015-01-10', periods=l, freq='D')
    data = pd.np.random.rand(l)
    return pd.Series(data,dr)

class TestSymbolAggregation(object):
    @classmethod
    def setup_class(self):

        ors = make_fake_feed_data(1).shift(1, freq='D')
        s1 = make_fake_feed_data(10)
        s2 = make_fake_feed_data(5)
        s3 = make_fake_feed_data(7)
        fls = make_fake_feed_data(1).shift(8, freq='D')

        s1.iloc[6] = pd.np.nan
        s1.iloc[8] = pd.np.nan

        cols = ['override_'] + [''] * 3
        cols = [c + "feed{0:03d}".format(i) for i, c in enumerate(cols)]
        cols = cols + ['failsafe_feed999']

        self.dft = pd.concat([ors, s1, s2, s3, fls], axis=1)
        self.dft.columns = cols

    def setup_method(self, method):
        self.df = self.dft.copy(deep=True)

    def test_priority_fill(self):

        df = self.df

        df['final'] = FeedAggregator('priority_fill').aggregate(df)

        assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
        assert df['final'].iloc[-1] == df['feed001'].iloc[-1]
        assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
        assert df['final'].iloc[-4] == df['feed003'].iloc[-4]

    def test_mean_fill(self):

        df = self.df

        df['final'] = FeedAggregator('mean_fill').aggregate(df)

        assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
        assert df['final'].iloc[-1] == df['feed001'].iloc[-1]
        assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
        assert df['final'].iloc[-4] == df['feed003'].iloc[-4]

        fstrow_mean = df[[c for c in df.columns if c[:4] == 'feed']].iloc[0].mean()
        assert df['final'].iloc[0] == fstrow_mean

        fifthrow_mean = (df['feed001'].iloc[5] + df['feed003'].iloc[5]) / 2
        assert round(df['final'].iloc[5],2) == round(fifthrow_mean,2)

    def test_median_fill(self):

        df = self.df

        df['final'] = FeedAggregator('median_fill').aggregate(df)

        assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
        assert df['final'].iloc[-1] == df['feed001'].iloc[-1]
        assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
        assert df['final'].iloc[-4] == df['feed003'].iloc[-4]

        fstrow = df[[c for c in df.columns if c[:4] == 'feed']].iloc[0]
        fstrow_med = fstrow.median()
        assert df['final'].iloc[0] == fstrow_med

        fifthrow_med = (df['feed001'].iloc[5] + df['feed003'].iloc[5]) / 2
        assert round(df['final'].iloc[5],2) == round(fifthrow_med,2)

    def test_most_populated(self):

        df = self.df

        df['final'] = FeedAggregator('most_populated').aggregate(df)

        assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
        assert df['final'].iloc[-1] == df['feed001'].iloc[-1]
        assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
        assert pd.isnull(df['final'].iloc[-4])

    def test_most_recent(self):

        df = self.df

        mr = FeedAggregator('most_recent')
        
        df.iloc[-1] = pd.np.nan
        df.iloc[-3] = pd.np.nan

        df['final'] = mr.aggregate(df)

        assert df['final'].iloc[1] == df['override_feed000'].iloc[1]
        assert df['final'].iloc[-4] == df['feed003'].iloc[-4]
        assert df['final'].iloc[-2] == df['failsafe_feed999'].iloc[-2]
        assert pd.isnull(df['final'].iloc[-1])
