Basic Usage
===========
These examples dramatically understate the utility of Trump's long term feature set.

Tesla Closing Price from Multi-Source
-------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, GoogleFinanceFT, YahooFinanceFT

   sm = SymbolManager()

   TSLA = sm.create(name = "TSLA", description = "Tesla Closing Price USD",
                   units = '$ / share')

   TSLA.add_tags(["stocks","US"])

   #Try Google First
   #If Google's feed has a problem, try Quandl's backup
   #If all else fails, use Yahoo's data...

   TSLA.add_feed(GoogleFinanceFT("TSLA")) # 'Close' is stored in the GoogleFinanceFT Template
   TSLA.add_feed(QuandlFT("GOOG/NASDAQ_TSLA",fieldname='Close'))
   TSLA.add_feed(YahooFinanceFT("TSLA"))  # 'Close' is stored in the YahooFinanceFT Template

   #All three are downloaded, with every cache instruction
   TSLA.cache() 

   # In the end, you're left with one clean pandas Series representing TSLA's closing
   # price, with source, munging, and validity parameters all stored persistently for future
   # re-caching.

   print TSLA.df.tail()

                 TSLA
   dateindex         
   2015-03-20  198.08
   2015-03-23  199.63
   2015-03-24  201.72
   2015-03-25  194.30
   2015-03-26  190.40 
   
   sm.finish()
   
Using the Symbol
~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   TSLA = sm.get("TSLA")

   #optional
   TSLA.cache()

   # Trump's plans for various aggregation, munging, and validity checking can
   # use the intelligence of multiple feeds to compare and clean up the data
   # if a variety common problems exist. These features are few months off,
   # but a priority in Trump's plans.
   
   # For instance (not implemented yet):
   
   if TSLA.validity('feeds_match'):
      #do stuff with clean data

   if TSLA.validity('todays_closing_price_reliable'):
      #do stuff with today's data point

   if TSLA.validity('local_calendar_check'):
      #handle international calendar issues 
   
   print TSLA.df.tail()
   
                 TSLA
   dateindex         
   2015-03-20  198.08
   2015-03-23  199.63
   2015-03-24  201.72
   2015-03-25  194.30
   2015-03-26  190.40  

   sm.finish()
   
Oil from Quandl & SQL Example
-----------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, SQLFT

   sm = SymbolManager()

   oil = sm.create(name = "oil_front_month",
                   description = "Crude Oil",
                   units = '$ / barrel')

   oil.add_tags(['commodity','oil','futures'])

   f1 = QuandlFT(r"CHRIS/CME_CL2",fieldname='Settle')
   f2 = SQLFT("SELECT date,data FROM test_oil_data;")

   oil.add_feed(f1)
   oil.add_feed(f2)

   oil.cache()

   print oil.df.tail()

   sm.finish()

Using the Symbol
~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   oil = sm.get("oil_front_month")

   #optional
   oil.cache()

   print oil.df.tail()

   sm.finish()
