
Aggregation
-----------

A Symbol's feeds are queried with each cache, then aggregated in 
a per-Symbol defined method.  The process relies on the pandas
Dataframe representation of the Symbol's datable.

The Datatables
**************

With every Symbol cache, a Dataframe is created, and stored in the database
in a table matching the symbol's name.  This table, is referred to as the datatable.
The Dataframe has a column for every feed, plus two for override and failsafe.
The datatable, has the same columns, plus one for the index, and the final data.
The final data column, is calculated by the specified aggregation function, definedat
at, or updated after, Symbol instantiation

Aggregation Methods
*******************

Trump currently has two types of aggregation methods:

1. Row-apply
2. Column-choose

As the names infer, the row-apply methods have one thing in common,
they build the final data values by looking at each row of the datatable, one at a time.
The column-choose methods, compare the data available in each column, then return an entire series.
Row-apply methods all take a pandas Series, and return a value.  Column-choose methods
all take a pandas Dataframe, and return a series. 

Row-apply functions are invoked using the pseudo code below:

.. code-block:: python
	
	df['final'] = df.apply(row_apply_method, axis=1)

Column-choose functions are invoked using the pseudo code below:

.. code-block:: python
	
	df['final'] = column_choose_method(df)

Both methods have access to the data in the override, and failsafe, columns so
it's technically possible to create a method which overloads the
behaviour of these columns. It is the responsibility of each method
to implement the override, and failsafe, logic. 

Apply-Row Methods
^^^^^^^^^^^^^^^^^

Each of these methods, can be thought of as a for-loop that looks at each
row of the datatable, then decides on the correct value for the final column,
on a row by row basis. 

The datatable, as a Dataframe, gets these methods applied.  The columns
are sorted prior to being passed.  So, the value at index 0, is always
the override datapoint, if it exists, and the value at index -1, is always
the failsafe datapoint, if it exists.  Everything else, that is, the feeds,
are in columns 1 through n, where n is the number of feeds.

.. automethod:: trump.extensions.symbol_aggs.ApplyRow.priority_fill

.. automethod:: trump.extensions.symbol_aggs.ApplyRow.mean_fill

.. automethod:: trump.extensions.symbol_aggs.ApplyRow.median_fill

.. automethod:: trump.extensions.symbol_aggs.ApplyRow.custom

.. note::

	The aggregation methods are organized in the code
	using private mixin classes.  The FeedAggregator object
	handles the implementation of every static method,
	based solely on it's name.  This means that
	any new methods added, must be unique to either mixin.

Choose-Column Methods
^^^^^^^^^^^^^^^^^^^^^

Each of these methods, can be thought of as a for-loop that looks at each
column of the datatable, then chooses the appropriate feed to use, as final.
They all still apply overrides and failsafes on a row-by-row basis.

The datatable, as a Dataframe, is passed to these methods in  a single call.

.. automethod:: trump.extensions.symbol_aggs.ChooseCol.most_populated

.. automethod:: trump.extensions.symbol_aggs.ChooseCol.most_recent

.. automethod:: trump.extensions.symbol_aggs.ChooseCol.custom

.. note::

	See the note in the previous section about custom method
	naming.