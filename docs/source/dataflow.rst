Dataflow
=========
The flow of information in Trump, is slightly unorthodox, because it's centralizes data by design.
The first-principles approach to using trump, excludes any usage of templates of anykind, and, would look something like this:

First Principles
---------------------

Using Trump's ORM, the process is something akin to:

1. Instantiate a new :py:class:`~trump.orm.Symbol`
2. Optionally, add some :py:class:`~trump.orm.SymbolTag`
3. Optionally, adjust the symbol's :py:class:`~trump.orm.Index` case and type
4. Optionally, adjust the symbol's :py:class:`~trump.orm.SymbolHandle` handlepoints
5. Instantiate one ore more :py:class:`~trump.orm.Feed` objects
6. For each Feed, update :py:class:`~trump.orm.FeedMeta`, :py:class:`~trump.orm.FeedSource` details
7. Optionally, adjust each feed's :py:class:`~trump.orm.FeedMunge` instructions
8. Optionally, adjust each feed's :py:class:`~trump.orm.FeedHandle` handlepoints
9. Anytime the data is potentially updated, cache the Symbol.  This process uses each feed's source to retrieve a fresh copy, and save the data and compute a final version in the symbol's datatable.
10. Any process, including non-python ones, can retrieve the data from the cached database table.
11. Any python application, can retrieve a pandas Series and check the Symbol's validity.
12. Detect problems, add :py:class:`~trump.orm.Override` and :py:class:`~trump.orm.Failsafe` objects to "fix" a Symbol's final result.

Template Based
-----------------------

By using, and setting up, Trump templates, step 0 and 1 of this process, replaces steps 1 to 8 of the first-principles approach.  Then, step 2 to 4 are the same as 10 to 12.

0. Create custom templates for common sources of proprietary.
1. Instantiate a new :py:class:`~trump.orm.Symbol` using a template containing Tag, Feed, Source and Handle settings.
2. Anytime the data is needed, cache the Symbol.  This process uses each feed's source to retrieve a fresh copy, and saves in the database where Trumpe is installed.
3. Any python application, can retrieve a pandas Series and check the Symbol's validity.
4. Detect problems, add :py:class:`~trump.orm.Override` and :py:class:`~trump.orm.Failsafe` objects to "fix" a Symbol's final result.

Caching
-----------

The cache process, is more than just caching.  When executed, data from each Feed is queried, and and munged according to predefined,
per-feed settings.  Then, it's concatenated into a pandas Dataframe. A :py:class:`~trump.indexing.IndexImplementor` corrects the index.
An aggregation method converts the dataframe into a single Series. Single values are overrode, and blanks get populated, based on any previously
defined :py:class:`~trump.orm.Override` and :py:class:`~trump.orm.FailSafe` associated with the symbol being cached.
This entire result is then stored in the symbol's datatable, where it can be quickly queried to either use the data, or run validity checks.
