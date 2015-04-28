# -*- coding: utf-8 -*-

from trump.orm import SymbolManager
from trump.templating import QuandlFT, QuandlSecureFT, SQLFT
from trump.tools.bitflags import  BitFlag
from datetime import datetime as dt

sm = SymbolManager()

oil = sm.create(name = "oil_front_month",
                description = "Crude Oil Futures, Continuous Contract #2 (CL2) (Front Month)",
                units = '$ / barrel')

oil.add_alias("OILA")
oil.add_tags(['commodity','oil'])

f1 = QuandlFT(r"CHRIS/CME_CL3",fieldname='Settle')
#f2 = QuandlSecureFT(r"CHRIS/CME_CL3",fieldname='Settle')
#f3 = QuandlSecureFT(r"NO_OIL_DATA",fieldname='Settle')
#f3 = SQLFT("SELECT date,data FROM test_oil_data;")

oil.add_feed(f1)
#oil.add_feed(f2)
#oil.add_feed(f3)

oil.feeds[0].handle.api_failure = BitFlag(0)
#oil.feeds[1].handle.api_failure = BitFlag(0)
oil.handle.feed_aggregation_problem = BitFlag({'raise' : True, 'stdout': True, 'warn': False})
#oil.feeds[0].handle.api_failure = BitFlag({'raise' : False, 'stdout': False, 'warn': True})

sm.complete()

df = oil.cache()

print oil.df.tail()
