# -*- coding: utf-8 -*-

from trump.orm import SymbolManager
from trump.templating import fQuandl, fQuandlSecure, fSQL
from trump.templating import mFFillRollingMean

from datetime import datetime as dt

sm = SymbolManager()

oil = sm.create(name = "oil_front_month",
                description = "Crude Oil Futures, Continuous Contract #2 (CL2) (Front Month)",
                freq = 'D',
                units = '$ / barrel')

oil.addAlias("OILA")
oil.addTags(['commodity','oil'])

f1 = fQuandl(r"CHRIS/CME_CL2",fieldname='Settle')
f2 = fQuandlSecure(r"CHRIS/CME_CL3",fieldname='Settle')
#f3 = fSQL("SELECT date,data FROM test_oil_data;")

m1 = mFFillRollingMean(window=5,min_periods=3,center=True)

oil.addFeed(f1,munging=m1)
#oil.addFeed(f2)
#oil.addFeed(f3)

#;oil.addOverride(dt(2015,1,6),50.0,user='Jeffor')
#oil.addFailSafe(dt(2015,1,6),45.0,user='Jefffs')

df = oil.cache()

print oil.df.tail()

sm.finish()
            