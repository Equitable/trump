# -*- coding: utf-8 -*-

from trump.orm import SymbolManager
from trump.templating import QuandlFT, GoogleFinanceFT, YahooFinanceFT

sm = SymbolManager()

TSLA = sm.create(name = "TSLA", description = "Tesla Closing Price USD",
                freq = 'B', units = '$ / share')

TSLA.add_tags(["stocks","US"])

#Try Google First
#If Google's feed has a problem, try Quandl's backup
#If all else fails, use Yahoo's data...

TSLA.add_feed(GoogleFinanceFT("TSLA"))
TSLA.add_feed(QuandlFT("GOOG/NASDAQ_TSLA",fieldname='Close'))
TSLA.add_feed(YahooFinanceFT("TSLA"))

#All three are downloaded, with every cache instruction
TSLA.cache()

# Trump's plans for various aggregation, munging, and validity checking can
# use the intelligence of multiple feeds to compare and clean up the data
# if a variety common problems exist. These features are few months off,
# but a priority in Trump's plans.

# In the end, you're left with one clean pandas Series representing TSLA's closing
# price, with source, munging, validity checks, all stored persistently for future
# re-caching.

print TSLA.df.tail()

sm.finish()
            