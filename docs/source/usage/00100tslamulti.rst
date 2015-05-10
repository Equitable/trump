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