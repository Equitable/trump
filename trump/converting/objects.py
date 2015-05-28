# -*- coding: utf-8 -*-
import pandas as pd
import Quandl as qdl

from datetime import datetime as dt

def recip(t):
    return t[1], t[0]

class CurPair(object):
    def __init__(self, sym):
        if len(sym) == 6:
            self.num, self.den = sym[3:], sym[:3]
        elif "//" in sym:
            self.num, self.den = sym.split("//")
        elif len(sym) == 2: #should be a tuple
            self.num, self.den = sym
            
    @property
    def pair(self):
        return (self.num, self.den)
    @property
    def inverse(self):
        return CurPair(self.pair[::-1])
    def __eq__(self, obj):
        if not isinstance(obj, CurPair):
            obj = CurPair(obj)
        return self.num == obj.num and self.den == obj.den
    def __gt__(self, obj):
        if self == obj:
            return 'equal'
        elif self == obj.inverse:
            return 'recip'
        elif self.den in obj.pair[0]:
            raise NotImplementedError("CurPair not done")
        
class FXConverter(object):
    def __init__(self):
        
        self.pairs = [('EUR','USD'),
                    ('USD','JPY'),
                    ('GBP','USD'),
                    ('AUD','USD'),
                    ('USD','CHF'),
                    ('NZD','USD'),
                    ('USD','CAD')]
        
        self.start = dt(2015,1,1)
        self.end = dt.now()

    def use_quandl_data(self, authtoken):
        """
        Use quandl data to build conversion table
        """
        dfs = {}
        st = self.start.strftime("%Y-%m-%d")
        at = authtoken
        for pair in self.pairs:
            symbol = "".join(pair)
            qsym = "CURRFX/{}".format(symbol)
            dfs[symbol] = qdl.get(qsym,authtoken=at, trim_start=st)['Rate']
            
        self.build_conversion_table(dfs)

    def use_trump_data(self, symbols):
        """
        Use trump data to build conversion table
        
        symbols : 
            list of symbols:
                will attempt to use units to build the conversion table,
                strings represent symbol names.
        """
        dfs = {sym.units : sym.df[sym.name] for sym in symbols}
               
        self.build_conversion_table(dfs)
        
    def build_conversion_table(self, dataframes):
        """
        Build conversion table from a dictionary of dataframes
        """
        self.data = pd.DataFrame(dataframes)
        tmp_pairs = [s.split("/") for s in self.data.columns]
        self.data.columns = pd.MultiIndex.from_tuples(tmp_pairs)
           
    def convert(self, data, denom, to):
        
        # We need to do this, cause humans are dumb
        if "/" in denom:
            denom = denom.split(r"/")[0]
        if "/" in to:
            to = to.split(r"/")[1]
            
        pair = (denom, to)
        
        if pair in self.data.columns:
            tmp = data.mul(self.data[pair], axis=0)
        elif recip(pair) in self.data.columns:
            tmp = data.mul(self.data[recip(pair)], axis=0)
        else:
            tmp = self.convert(data, denom, 'USD')
            tmp = self.convert(tmp, 'USD', to)
        
        return tmp
        
if __name__ == '__main__':
    FXc = FXConverter()
    FXc.use_quandl_data('TODO')
    
    gold = qdl.get('LBMA/GOLD', authtoken='TODO')
    g_eur = gold['EURO (PM)']
    g_gbp = gold['GBP (PM)']
    g_usd = gold['USD (PM)']