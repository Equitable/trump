=====
Trump
=====

------------------------------------------
Persistent Objectification of Indexed Data
------------------------------------------

Trump is a framework for objectifying data, with the goal of centralizing the responsibility of 
managing feeds, munging, calculating and checking data, upstream of any application or user requirement.

Inside the Trump framework, a symbol refers to one or more data feeds, each with their own instructions
saved for retrieving data.  Once it's retrieved by Trump, depending on the attributes of the symbol,
it gets munged, aggregated, checked, and cached.  Downstream users are free to query the existing cache,
force a re-cache, or check any property of the data prior to using it.
 
System Admins can systematically detect problems in advance, via common integrity checks of the data,
then optionally schedule the re-cache by tag or symbol name.  Users and admins have the ability to manually
override problems if they exist, with a specific feed, in a way that is centralized, audited, and backed-up.

With a focus on business processes, Trump's long run goals enable data feeds to be:

* Prioritized, flexibly - a symbol can be associated with multiple data source for a variety of reasons including redundancy, calculations, or optionality.
* Modified, reliably - a symbol's data feeds can be changed out, without any changes requiring testing to the downstream application or user.
* Verified, systematically - a variety of common data processing checks are performed as the symbol's data is cached.
* Audited, quickly - alerts and reports all become possible to assess integrity or inspect where manual over-rides have been performed.
* Aggregated, intelligently - on a symbol by symbol basis, feeds can be combined and used in an extensible number of ways.
* Customized, dynamically - extensibility is possible at the templating, munging, aggregation, and validity steps.

Planning
========

Trump's initial priority is numeric and monotonic timeseries data, but written with the
future in mind to eventually work with any object as data, and any object as an index.
Eliminating the non-monotonic assumption is a lower priority. Code legibility is paramount,
with speed improvements deferred.

The initial release of Trump is planned to include the basics of the framework, with the low-hanging
fruit deferred to later in 2015 or early 2016.  A Web UI currently exists, but is outside the scope
of Trump until user demand justifies it's release.  This is mainly a technical-resource based decision.

Timing 
------

Finishing the planning phase should be mid-March 2015; the code base is under rapid expansion 
and changes.  Building the testing framework is planned for April 2015, with the hopes of participating
in "Adopty py.test".  The first release is optimistically scheduled for early June 2015, with 
the fractions of the initial goals completed:

- Prioritization
  - Priority Index-based
  - Priority Feed-Based
  - Latest Available Feed-Based
- Modified
  - Override Index-based
  - Failsafe Index-based
- Verified  - Feed Compare Index-based
  - Feed Compare Feed-based
- Audited (Not Started)
- Aggregated
  - Mean
  - Median
  - Basic Pandas Functions (Eg. pct_change())
- Customized
  - Framework ready

Dependencies
============
- `Pandas <http://pandas.pydata.org/>`_ (Tested with >= 15.2)
- `SQLAlchemy <http://sqlalchemy.org/>`_ (Tested with >= 0.9)
- `Smuggle <https://pypi.python.org/pypi/smuggle>`_ (Tested with >= 0.2.0)

Requirements
=============
* Python 2.7; Support for Python 3.3 or 3.4 should be do-able, if there was interest.
* A relational database supported by SQLAlchemy.

Basic Usage
===========
Coming soon.

Installation
=============
Check back March 22nd or slightly after.

Documentation
=============
Check back March 22nd or slightly after.  For now, see the pdf in the prototype branch.

Contributing
============
Coming soon.

License
=======
BSD-3 clause

Background
==========
The prototype for ``Trump`` was built at Equitable Life of Canada in 2014 by Jeffrey McLarty, CFA 
and Derek Vinke, CFA. 
