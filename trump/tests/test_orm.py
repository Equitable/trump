from ..orm import SymbolManager

from ..templating.templates import GoogleFinanceFT, SimpleExampleMT

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