Data From CSV, with a frequency-specified index
-----------------------------------------------

Adding the Symbol
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager
   
   #Import the CSV Feed Template
   from trump.templating import CSVFT
   
   #Import the Forward-Fill Index Template
   from trump.templating import FFillIT

   sm = SymbolManager()

   sym = sm.create(name = "DailyDataTurnedWeekly")
   
   f1 = CSVFT('somedata.csv', 'ColumnName', parse_dates=0, index_col=0)
   
   sym.add_feed(f1)
   
   weeklyind = FFillIT('W')
   sym.set_indexing(weekly)

   sym.cache()
   
   sm.finish()

Using the Symbol
~~~~~~~~~~~~~~~~

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   sym = sm.get("DailyDataTurnedWeekly")

   #optional
   oil.cache()

   print sym.df.index
   # <class 'pandas.tseries.index.DatetimeIndex'>   
   # [2010-01-03, ..., 2010-01-17] 
   # Length: 3, Freq: W-SUN, Timezone: None

   sm.finish()