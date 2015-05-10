Basic Usage
===========
These examples dramatically understate the utility of Trump's long term feature set.

Tesla Closing Price from Multiple Sources
-----------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, GoogleFinanceFT, YahooFinanceFT,
                                DateExistsVT, FeedMatchVT

   sm = SymbolManager()

   TSLA = sm.create(name = "TSLA",
                    description = "Tesla Closing Price USD",
                    units = '$ / share')

   TSLA.add_tags(["stocks","US"])

   #Try Google First
   #If Google's feed has a problem, try Quandl's backup
   #If all else fails, use Yahoo's data...

   # 'Close' is stored in the GoogleFinanceFT Template
   TSLA.add_feed(GoogleFinanceFT("TSLA")) 
   
   TSLA.add_feed(QuandlFT("GOOG/NASDAQ_TSLA", fieldname='Close'))

   # 'Close' is stored in the YahooFinanceFT Template
   TSLA.add_feed(YahooFinanceFT("TSLA"))  
   
   
   #All three are downloaded, with every cache instruction
   TSLA.cache() 

   # In the end, the result is one clean pandas Series representing 
   # TSLA's closing price, with source, munging, and validity parameters
   # all stored persistently for future
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
   
   print TSLA.df.tail()
   
                 TSLA
   dateindex         
   2015-03-20  198.08
   2015-03-23  199.63
   2015-03-24  201.72
   2015-03-25  194.30
   2015-03-26  190.40  

   sm.finish()


Tesla Closing Price from Two Sources, With Validity Checks
----------------------------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, GoogleFinanceFT, 
                                DateExistsVT, FeedMatchVT

   sm = SymbolManager()

   TSLA = sm.create(name = "TSLA",
                    description = "Tesla Closing Price USD",
                    units = '$ / share')

   TSLA.add_feed(GoogleFinanceFT("TSLA")) 
   TSLA.add_feed(QuandlFT("GOOG/NASDAQ_TSLA", fieldname='Close'))
   
   # Tell trump, to check the first and second feed,
   # because they should be equal.

   validity_settings = FeedsMatchVT(1, 2)
   TSLA.add_validity(validity_settings)
   
   # Tell trump, to make sure we have a data point for the current day
   # any time we check validity. 
      
   validity_settings = DateExistsVT('today')
   TSLA.add_validity(validity_settings)

   # By default, the cache process checks the validity settings
   # or will raise/log/warn/print/etc. based on the appropriate
   # handler for validity.
   
   # Since we're going to check validity, with a bit more
   # granularity upstream/later, we can skip it during the cache process
   # by setting it to False.
   
   TSLA.cache(checkvalidty=False) 
   
   sm.finish()
   
Using the Symbol
~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   TSLA = sm.get("TSLA")

   #optional
   TSLA.cache()

   #There are a few options, to check the data...
   
   #Individual validity checks can be ran, with the 
   # settings stored persistently in the object
   
   # Eg 1
   if TSLA.check_validity('FeedMatch'):
      #do stuff with clean data

   # Eg 2
   if TSLA.check_validity('DateExists'):
      #do stuff with today's data point

   # Or, all the validity checks with their 
   # respective settings can be ran with one simple
   # property:
   
   if TSLA.isvalid:
      #do stuff with knowing both feeds match, and 
	  # a datapoint for today exists.
   
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
