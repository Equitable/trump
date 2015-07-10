from trump.orm import SetupTrump, SymbolManager
from trump.tools.metamatrix import MetaMatrix

import pandas as pd
from pandas.util.testing import assert_frame_equal

class TestToolsSQLA(object):
    
    def setup_method(self, test_method):
        self.eng = SetupTrump()
        self.sm = SymbolManager(self.eng)

    def test_metamatrix(self):
        tikrs = [x * 3 for x in list('jkl')]
        syms = []
        for s in tikrs:
            sym = self.sm.create(s, overwrite=True)
            sym.add_meta(alpha='a', beta='b', charlie='c')
            syms.append(sym)
        
        mm = MetaMatrix(syms)
        
        mmr = mm(['alpha','beta'])
        
        exp = pd.DataFrame({'alpha' : ['a'] * 3,
                            'beta' : ['b'] * 3}, index = tikrs)
        
        exp.index.name = 'trumpsym'        
        assert_frame_equal(mmr, exp)