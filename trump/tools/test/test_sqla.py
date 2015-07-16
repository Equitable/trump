from trump.orm import SetupTrump, SymbolManager

class TestToolsSQLA(object):
    
    def setup_method(self, test_method):
        self.eng = SetupTrump()
        self.sm = SymbolManager(self.eng)

    def test_repr_mixin(self):
        sym = self.sm.create("testsym", overwrite=True)
        assert repr(sym) == """Symbol(name=u'testsym', description=None, units=None, agg_method=u'priority_fill', freshthresh=0)"""
        