
Datatables
----------

With every Symbol cache, a Dataframe is created, and stored in the database
in a table matching the symbol's name.  The Dataframe has a column for 
every feed, plus two for override and failsafe.  The datatable, has the same
columns, plus one for the index, and the final data. The final data column, is
calculated by the specified aggregation function, at Symbol instantiation
(or it can be changed after instantiation.)

Row-apply vs Column-choose
--------------------------

Trump currently has two types of aggregation functions:

1. Row-apply
2. Column-choose

As the names infer, the row-apply methods have one thing in common,
they build the final data column looking at one row of the datatable at a time.
The column-choose methods, compare the data available in each column, then return a series.
Row-apply methods all take a pandas Series, and return a value.  Column-choose methods
all take a pandas Dataframe, and return a series. 

Row-apply functions are invoked using:

.. code-block:: python
	
	df['final'] = df.apply(func, axis=1)

Column-choose functions are invoked using:

.. code-block:: python
	
	df['final'] = func(df)

Both methods have access to the data in the override, and failsafe, so
it's technically possible to create a method which overrides the default
behaviour of these values, and it is the responsibility of each method
to implement the override, and failsafe, logic. 

Row-apply Methods
*****************

TODO

priority_fill
^^^^^^^^^^^^^

TODO


mean_fill
^^^^^^^^^

TODO

median_fill
^^^^^^^^^^^

TODO

custom 
^^^^^^

easy to make...

Column-choose Methods
*********************

TODO

most_populated
^^^^^^^^^^^^^^

TODO

most_recent
^^^^^^^^^^^

TODO

custom 
^^^^^^