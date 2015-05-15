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

    def _get_quandl_data(self, authtoken):
        dfs = {}
        st = self.start.strftime("%Y-%m-%d")
        at = authtoken
        for pair in self.pairs:
            symbol = "".join(pair)
            print "fetching {}".format(symbol)
            qsym = "CURRFX/{}".format(symbol)
            dfs[symbol] = q.get(qsym,authtoken=at, trim_start=st)['Rate']

        self.data = pd.DataFrame(dfs)
        tmp_pairs = [(s[:3],s[3:]) for s in self.data.columns]
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
        

FXc = FXConverter()
FXc._get_quandl_data('TODO')

gold = q.get('LBMA/GOLD', authtoken='TODO')
g_eur = gold['EURO (PM)']
g_gbp = gold['GBP (PM)']
g_usd = gold['USD (PM)']