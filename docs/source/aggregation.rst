
Aggregation Methods
-------------------

Trump currently has two types of aggregation methods:

1. Apply-Row
2. Choose-Column

As the names infer, the apply-row methods have one thing in common,
they build the final data values by looking at each row of the datatable, one at a time.
The choose-column methods, compare the data available in each column, then return an entire series.
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

.. automethod:: trump.aggregation.symbol_aggs.ApplyRow.priority_fill

.. automethod:: trump.aggregation.symbol_aggs.ApplyRow.mean_fill

.. automethod:: trump.aggregation.symbol_aggs.ApplyRow.median_fill

.. automethod:: trump.aggregation.symbol_aggs.ApplyRow.custom

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

.. automethod:: trump.aggregation.symbol_aggs.ChooseCol.most_populated

.. automethod:: trump.aggregation.symbol_aggs.ChooseCol.most_recent

.. automethod:: trump.aggregation.symbol_aggs.ChooseCol.custom

.. note::

	See the note in the previous section about custom method
	naming.