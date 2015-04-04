# -*- coding: utf-8 -*-

from trump.orm import SymbolManager
from trump.templating import QuandlFT, QuandlSecureFT, SQLFT
from trump.tools.bitflags import  BitFlag
from datetime import datetime as dt

sm = SymbolManager()

oil = sm.create(name = "oil_front_month", overwrite=True)

f1 = QuandlFT(r"CHRIS/CME_CL3",fieldname='Settle')

oil.add_feed(f1)

oil.cache()

#print oil.data()
print oil.df.tail()

oil._reset_datatable()

oil.cache()

print oil.df.tail()