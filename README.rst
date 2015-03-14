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
in `Adopty py.test <http://pytest.org/latest/adopt.html>`_.  The first release is optimistically scheduled for early June 2015, with 
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
* A relational database supported by SQLAlchemy.  The first database with guaranteed support is PostGreSQL

Basic Usage
===========
Coming soon.

Installation
=============
Check back March 22nd or slightly after.  See the configuration section of the documentation,
for the instructions to follow post install.

The bare minimum requirement is to create a trump.cfg file from the trump.cfg_sample in /config folder.
All it needs is a SQLAlchemy engine string where it can store Trump.

*.cfg files are ignored by this repo.  *.cfg_sample files aren't.

Trump Configuration (/config)
-----------------------------
This file should be renamed to trump.cfg.  These are the settings for connecting to a database with a user that has...

Trump Templating Settings (/settings)
-------------------------------------
The cfg_sample files need to be renamed to cfg, in here need to be matched with their respective trump template...

Documentation
=============
Check back March 22nd or slightly after.  For now, see the pdf in the prototype branch.

Configuration
-------------

Configuring Trump
-----------------
Trump needs at the very least, a SQL Alchemy connection string with read+write-level access to the
database where it can install itself.  This can be populated in config/trump.cfg.

Configuring Data Sources
------------------------

Sources of data feeds map to their respective case sensitive file *.cfg file in the configuration folder.
Trump will use parameters for a source in the following order:

1. Specified explicitly when a template is used. (Eg. table name)
2. Specified implicitly using logic derived in the template based on the template itself or argument values passed. (Eg. Database Names)
3. Specified implicitly using a argument's default value. (Eg. database host, port)
4. Specified on disk via the source's configuration file. (Eg. authentication keys and passwords)
5. Specified on disk encrypted sources via an encrypted config file. (Eg. top-secret passwords) (Not yet implemented)

If it relies on #4 or #5, the info will not be stored in the database.  Instead, it will be looked
up at runtime from the config file.  This means that the config file values can be changed 
post symbol creation, but the specific arguments can not be.

There is nothing in stone, saying that a password can't be hardcoded into a template, just the 
same as there is nothing in stone, dictating that a tablename can't be included in a config file.

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
