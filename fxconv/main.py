# -*- coding: utf-8 -*-
"""
Created on Thu May 14 22:14:12 2015

@author: Jeffrey
"""
import pandas as pd
import Quandl as q

from datetime import datetime as dt

default_start = dt(2015,1,1)
default_end = dt.now()

def recip(t):
    return t[1], t[0]
    
class FXConverter(object):
    def __init__(self):
        
        self.pairs = [('EUR','USD'),
                    ('USD','JPY'),
                    ('GBP','USD'),
                    ('AUD','USD'),
                    ('USD','CHF'),
                    ('NZD','USD'),
                    ('USD','CAD')]
        
        self.start = default_start
        self.end = default_end

    def get_quandl_data(self, authtoken):
        """
        Use quandl data to build conversion table
        """
        dfs = {}
        st = self.start.strftime("%Y-%m-%d")
        at = authtoken
        for pair in self.pairs:
            symbol = "".join(pair)
            print "fetching {}".format(symbol)
            qsym = "CURRFX/{}".format(symbol)
            dfs[symbol] = q.get(qsym,authtoken=at, trim_start=st)['Rate']
            
        self.build_conversion_table(dfs)

    def get_trump_data(self, symbols):
        """
        Use trump data to build conversion table
        
        symbols : 
            string
                will treat as tag, query all, then use those plus
                their units to build conversion table.
            list of strings/symbols:
                will attempt to use units to build the conversion table,
                strings represent symbol names.
            dict of strings/symbols:
                keys represent pairs, values represent symbols,
                to use to build the currency
        """
        dfs = {}
        if isinstance(symbols, (str, unicode)):
            raise NotImplementedError()
        elif isinstance(symbols, (list, tuple)):
            raise NotImplementedError()
        elif isinstance(symbols, dict):
            raise NotImplementedError()
        
        self.build_conversion_table(dfs)
        
    def build_conversion_table(self, dataframes):
        """
        Build conversion table from a dictionary of dataframes
        """
        self.data = pd.DataFrame(dataframes)
        tmp_pairs = [(s[:3], s[3:]) for s in self.data.columns]
        self.data.columns = pd.MultiIndex.from_tuples(tmp_pairs)
    
    def convert(self, data, denom, to):
        
        pair = (denom, to)
        
        if pair in self.data.columns:
            tmp = data.mul(self.data[pair])
        elif recip(pair) in self.data.columns:
            tmp = data.div(self.data[pair])
        else:
            tmp = self.convert(data, denom, 'USD')
            tmp = self.convert(tmp, 'USD', to)
        
        return tmp
        
if __name__ == '__main__':
    FXc = FXConverter()
    FXc.get_quandl_data('TODO')
    
    gold = q.get('LBMA/GOLD', authtoken='TODO')
    g_eur = gold['EURO (PM)']
    g_gbp = gold['GBP (PM)']
    g_usd = gold['USD (PM)']