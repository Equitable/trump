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
        # print "Trying to convert", denom, to
    
        # We need to do this, cause humans are dumb,
        if "/" in denom:
            denom = denom.split(r"/")[0]
        if "/" in to:
            a,b = to.split(r"/")
            if b == 'unit':
                to = a
            else:
                to = b

        pair = (denom, to)
        
        denusd = (denom, 'USD')
        usdto = ('USD', to)
        
        #print "Trying to convert..." + str(pair)
        #print list(self.data.columns)
        #print pair in self.data.columns
        #print recip(pair) in self.data.columns
        
        pairs = self.data.columns
        
        if denom == to:
            tmp = data
        elif pair in pairs:
            tmp = data.div(self.data[pair], axis=0)
        elif recip(pair) in pairs:
            tmp = data.mul(self.data[recip(pair)], axis=0)
        elif ((denusd in pairs) or (recip(denusd) in pairs)) and \
             ((usdto  in pairs) or (recip(usdto)  in pairs)):
            tmp = self.convert(data, denom, 'USD')
            tmp = self.convert(tmp, 'USD', to)
        else:
            raise Exception ("Converter has insufficient data to process {} to {}".format(denom,to))

        return tmp
        
if __name__ == '__main__':
    FXc = FXConverter()
    FXc.use_quandl_data('TODO')
    
    gold = qdl.get('LBMA/GOLD', authtoken='TODO')
    g_eur = gold['EURO (PM)']
    g_gbp = gold['GBP (PM)']
    g_usd = gold['USD (PM)']