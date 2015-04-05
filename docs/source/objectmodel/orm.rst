Object Model
============

.. image:: sqla-orm.png

Symbol Manager
------------------------

.. autoclass:: trump.orm.SymbolManager
   :members: create, delete, get, complete, finish

Symbols
------------
   
.. autoclass:: trump.orm.Symbol
   :members: cache, describe

.. autoclass:: trump.orm.SymbolTag

.. autoclass:: trump.orm.SymbolHandle

Indicies
~~~~~~~~

.. autoclass:: trump.orm.Index
   :members: setkwargs, getkwargs

.. autoclass:: trump.orm.IndexKwarg
   :members: setval, val

Index Types
~~~~~~~~~~~

.. automodule :: trump.indexing

Feeds
--------

.. autoclass:: trump.orm.Feed
   :members: cache

.. autoclass:: trump.orm.FeedMeta

.. autoclass:: trump.orm.FeedMunge

.. autoclass:: trump.orm.FeedMungeArg

.. autoclass:: trump.orm.FeedHandle

Centralized Data Editing
----------------------------------

Each trump datatable comes with two extra columns beyond the feeds, index and final.  

The two columns are populated by any existing overrides and failsafes, which survive
caching, and modification to feeds.  

The Override will get applied blindly regardless of feeds, and the failsafes are used
only when data isn't availabe.  Once it becomes available for a specific index in the datatable,
the failsafe is ignored.

.. autoclass:: trump.orm.Override

.. autoclass:: trump.orm.FailSafe

Error Handling
--------------------

The Symbol & Feed objects have a single SymbolHandle and FeedHandle object accessed
via their .handle attribute. They both work identically. The only difference is the
column names that each have.  Each column, aside from symname,
represents a checkpoint during caching, which could cause errors external to trump.

The integer stored in each column, is a serialized BitFlag object, which is uses bit-wise
logic to save the settings associated with what to do upon an exception.

The Symbol's possible exception-inducing checkpoints include:

- caching (of feeds)
- concatenation (of feeds)
- aggregation (of final value column)
- validity_check

The Feed's possible exception-inducing checkpoints include:

- api_failure
- empty_feed
- index_type_problem
- index_property_problem
- data_type_problem
- monounique

For example, if a feed source is prone to problems, set the api_failure to print the trace by setting the BitFlag object's 'stdout' flag to True, and the other flags to False.
If there's a problem, Trump will attempt to continue, and hope that there is another feed with good data available.  However, if a source should be reliably available,
you may want to set the BitFlag object's 'raise' flag to True.

BitFlags
------------

There are two objects which make the BitFlag implementation work.  There is the BitFlag python object, which converts dictionaries and integers to bitwise logic, and then there is the BitFlagType which give SQLAlchemy the ability to handle a BitFlag object.

.. autoclass:: trump.tools.bitflags.BitFlag
  :members: __init__, bin, bin_str, asdict, __and__, __or__

.. autoclass:: trump.tools.bitflags.BitFlagType

