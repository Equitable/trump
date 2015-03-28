Basic Usage
===========
This example dramatically understates the utility of Trump's long term feature set.

Adding a Symbol
---------------

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, SQLFT

   sm = SymbolManager()

   oil = sm.create(name = "oil_front_month",
                   description = "Crude Oil",
                   freq = 'D',
                   units = '$ / barrel')

   oil.add_tags(['commodity','oil','futures'])

   f1 = QuandlFT(r"CHRIS/CME_CL2",fieldname='Settle')
   f2 = SQLFT("SELECT date,data FROM test_oil_data;")

   oil.add_feed(f1)
   oil.add_feed(f2)

   oil.cache()

   print oil.df.tail()
   
Using a Symbol
--------------

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   oil = sm.get("oil_front_month")

   #optional
   oil.cache()

   print oil.df.tail()