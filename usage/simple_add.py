# -*- coding: utf-8 -*-

from trump.orm import SymbolManager
from trump.templating import QuandlFT, QuandlSecureFT, SQLFT
from datetime import datetime as dt

sm = SymbolManager()

oil = sm.create(name = "oil_front_month",
                description = "Crude Oil Futures, Continuous Contract #2 (CL2) (Front Month)",
                units = '$ / barrel')

oil.add_alias("OILA")
oil.add_tags(['commodity','oil'])

f1 = QuandlFT(r"CHRIS/CME_CL2",fieldname='Settle')
f2 = QuandlSecureFT(r"CHRIS/CME_CL3",fieldname='Settle')
f3 = SQLFT("SELECT date,data FROM test_oil_data;")

oil.add_feed(f1)
oil.add_feed(f2)
oil.add_feed(f3)

oil.add_override(dt(2015,1,6),50.0,user='Jeffor')
oil.add_fail_safe(dt(2015,1,6),45.0,user='Jefffs')

df = oil.cache()

print oil.df.tail()
            