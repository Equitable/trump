Data Flow
=========
Trump centralizes the flow of information using two concepts:

1. Objectification
2. Caching

Objectification
---------------

The objectification happens via an addition-like process entailing the instantiation of one or more symbols.  
The objectification enables downstream applications to work with symbol names in order to force the caching, and be served reliable data.

There are two approaches to perform the objectification instantiation of Symbols

1. First Principles (from ORM)
2. Template Based (from Special Python Classes + ORM)
 
First Principles
^^^^^^^^^^^^^^^^

The first principles approach to using Trump is basically direct access to the SQLAlchemy-based object-relational model.
It's time consuming to develop with, but necessary to understand in order to design new intelligent templates.

Using Trump's ORM, the process is something akin to:

For Every Symbol:

	1. Instantiate a new :py:class:`~trump.orm.Symbol`
	2. Optionally, add some :py:class:`~trump.orm.SymbolTag`
	3. Optionally, adjust the symbol's :py:class:`~trump.orm.Index` case and type
	4. Optionally, adjust the symbol's :py:class:`~trump.orm.SymbolHandle` handlepoints
	5. Instantiate one ore more :py:class:`~trump.orm.Feed` objects
	6. For each Feed, update :py:class:`~trump.orm.FeedMeta`, :py:class:`~trump.orm.FeedSource` details
	7. Optionally, adjust each feed's :py:class:`~trump.orm.FeedMunge` instructions
	8. Optionally, adjust each feed's :py:class:`~trump.orm.FeedHandle` handlepoints
	9. Optionally, adjust each Symbol's :py:class:`~trump.orm.SymbolValidity` instructions

Template Based
^^^^^^^^^^^^^^

By setting up, and using Trump template classes, the two steps below replace steps 1 to 8 of the first principles approach. 

For Every Kind of Symbol:

	1. Create custom templates for common sources of proprietary data.

For Every Symbol:

	2. Instantiate a new :py:class:`~trump.orm.Symbol` using a template containing Tag, Feed, Source, Handle, Validity settings.
	3. Tweak any details uncovered by the chosen templates for the symbol, or any of it's feeds.

In practice, it's inevitable that templates will be used where possible, and do the heavy lifting of instantiation, but tweaks to each symbol would be made post-instantiation.	

Caching
-------

The cache process, is more than just caching, but that's the main purpose.  When executed, data from each Feed is queried, and munged according to predefined instructions,
on a per-feed basis.  Then, it's concatenated into a pandas Dataframe. A :py:class:`~trump.indexing.IndexImplementor` corrects the index.
An aggregation method converts the Dataframe into a single Series. Single values are overrode, and blanks get populated, based on any previously
defined :py:class:`~trump.orm.Override` and :py:class:`~trump.orm.FailSafe` associated with the symbol being cached.
This entire result is then stored in the symbol's datatable, where it can be quickly checked for validity and served to applications.
