from ..orm import SymbolManager

from ..templating.templates import GoogleFinanceFT

class TestORM(object):

    def test_symbol_creation(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA")

        sym.add_feed(fd)

        sym.cache()

        assert sym.df.ix['2015-04-10'][0] == 210.90