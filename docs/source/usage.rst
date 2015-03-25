Basic Usage
===========
This example dramatically understates the utility of Trump's long term feature set.

Adding a Symbol
---------------

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import fQuandl, fSQL

   sm = SymbolManager()

   oil = sm.create(name = "oil_front_month",
                   description = "Crude Oil",
                   freq = 'D',
                   units = '$ / barrel')

   oil.addTags(['commodity','oil','futures'])

   f1 = fQuandl(r"CHRIS/CME_CL2",fieldname='Settle')
   f2 = fSQL("SELECT date,data FROM test_oil_data;")

   oil.addFeed(f1)
   oil.addFeed(f2)

   oil.cache()

   print oil.df.tail()

   sm.finish()

Using a Symbol
--------------

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   oil = sm.get("oil_front_month")

   #optional
   oil.cache()

   print oil.df.tail()

   sm.finish()
