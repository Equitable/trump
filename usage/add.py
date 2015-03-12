# -*- coding: utf-8 -*-
"""
Created on Sun Jan 04 08:56:07 2015

@author: Jeffrey
"""

from trump.orm import SymbolManager


from trump.templating import fQuandl, mAddFFillMult

from datetime import datetime as dt

from collections import namedtuple

info = namedtuple('info',['description','ticker'])

oil = {"EU" : [info("Europe Brent Crude Oil Spot Price FOB", r"DOE/RBRTE")],
       "US" : [info("WTI Crude Oil Spot Price Cushing, OK FOB", r"DOE/RWTC")],
       "CONT" : [info("Crude Oil Futures, Continuous Contracts",r"CHRIS/CME_CL1"),
                info("Crude Oil Futures, Continuous Contract #2 (CL2) (Front Month)",r"CHRIS/CME_CL2")]}

sm = SymbolManager()

rawmunging = False
templatedmunging = True

if rawmunging:
    for oil_sym,oil_info_l in oil.iteritems():
        new_sym = sm.create("oil_" + oil_sym,"Quandl - " + oil_info_l[0].description,'D','$ / barrel')
        for oil_info in oil_info_l:
            f = fQuandl(oil_info.ticker,fieldname='Settle')
    
            f.addMunging('crop_dates',{'start' : '2000-01-01', 'end' : '2015-01-01'})
            f.addMunging('multiply_const',3)
    
            new_sym.addFeed(f,fillna={'method' : 'ffill'},exp_const=(3,['a','b','c'],{'n' : 123}),add_const={'n' : 55})
        new_sym.addAlias(oil_sym + "_oil")
        new_sym.addTags(['commodity','oil','quandl'])
        
        if oil_sym == 'CONT':
            new_sym.addOverride(dt(2015,1,6),50.0,user='Jeffor')
            new_sym.addFailSafe(dt(2015,1,6),45.0,user='Jefffs')
            
elif templatedmunging:
    for oil_sym,oil_info_l in oil.iteritems():
        new_sym = sm.create("oil_" + oil_sym,"Quandl - " + oil_info_l[0].description,'D','$ / barrel')
        for oil_info in oil_info_l:
            f = fQuandl(oil_info.ticker,fieldname='Settle')
            m = mAddFFillMult(5.0,mult=2.5)
            new_sym.addFeed(f,munging=m)
        new_sym.addAlias(oil_sym + "_oil")
        new_sym.addTags(['commodity','oil','quandl'])
        
        if oil_sym == 'CONT':
            new_sym.addOverride(dt(2015,1,6),50.0,user='Jeffor')
            new_sym.addFailSafe(dt(2015,1,6),45.0,user='Jefffs')