from ..orm import SymbolManager

from ..templating.templates import GoogleFinanceFT, YahooFinanceFT,\
    SimpleExampleMT

class TestORM(object):

    def test_symbol_creation(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA")

        sym.add_feed(fd)

        sym.cache()

        assert sym.df.ix['2015-04-10'][0] == 210.90

    def test_symbol_munging_mod(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fdtemp = GoogleFinanceFT("TSLA")

        mgtemp = SimpleExampleMT(5,5)

        sym.add_feed(fdtemp,munging=mgtemp)

        sym.cache()

        df = sym.df
        assert round(df.ix['2015-03-20'][0], 4) == round(0.031638, 4)

    def test_symbol_frequency_mod(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA")

        sym.add_feed(fd)

        sym.index.case = "asfreq"
        sym.index.setkwargs(freq='M', method='ffill')
        sm.ses.commit()

        sym.cache()

        df = sym.df
        assert df.ix['2015-03-31'][0] == 188.77

        assert df.index.freq == 'M'

    def test_two_symbols(self):

        sm = SymbolManager()

        sym = sm.create("MSFT", overwrite=True)

        fdgoog = GoogleFinanceFT("MSFT", start='2015-03-01', end='2015-03-10')
        fdyhoo = YahooFinanceFT("MSFT", start='2015-03-01', end='2015-03-14')

        sym.add_feed(fdgoog)
        sym.add_feed(fdyhoo)

        sym.cache()

        ans = sym.alldata()

        # the 13th is the last row, and it should be blank because
        # we only fetched through the 10th.
        print ans[-5]
        print ans[-1]
        assert ans[-1][-3] is None

        df = sym.df

        assert sym.n_feeds == 2
        assert round(df.ix['2015-03-13'][0], 2) == 41.38

    def test_tags_and_search(self):

        sm = SymbolManager()

        sym = sm.create("MSFT", overwrite=True)

        fdmsft = YahooFinanceFT("MSFT")

        sym.add_feed(fdmsft)

        sym.add_tags(['tech','software'])

        results = sm.search_tag('tech')

        msft = results[0]

        msft.cache()

        assert msft.df.ix['2015-04-10'][0] == 41.72

        results = sm.search_tag('soft%')

        msft2 = results[0]

        assert msft2 is msft

        msft.del_tags('tech')

        results = sm.search_tag('tech')

        assert len(results) == 0