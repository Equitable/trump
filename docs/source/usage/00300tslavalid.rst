Tesla Closing Price from Two Sources, With Validity Checks
----------------------------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, GoogleFinanceFT, 
                                DateExistsVT, FeedsMatchVT

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
   if TSLA.check_validity('FeedsMatch'):
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
 