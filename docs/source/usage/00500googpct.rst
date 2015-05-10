Google Stock Price Daily Percent Change Munging
-----------------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import YahooFinaceFT

   sm = SymbolManager()

   GOOGpct = sm.create(name = "GOOGpct",
                       description = "Google Percent Change")

   fdtemp = YahooFinanceFT("GOOG")

   mgtemp = PctChangeMT()

   GOOGpct.add_feed(fdtemp, munging=mgtemp)

   
Using the Symbol
~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   GOOG = sm.get("GOOGpct")

   #optional
   GOOG.cache()
   
   print GOOG.df.tail()

   #             GOOGpct
   # 2015-05-04  0.005354
   # 2015-05-05 -0.018455
   # 2015-05-06 -0.012396
   # 2015-05-07  0.012361
   # 2015-05-08  0.014170