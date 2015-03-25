# -*- coding: utf-8 -*-

from trump.orm import SymbolManager

sm = SymbolManager()

oil = sm.get("oil_front_month")

oil.cache()

print oil.df.tail()

sm.finish()