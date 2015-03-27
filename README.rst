=====
Trump
=====

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/Equitable/trump
   :target: https://gitter.im/Equitable/trump?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://readthedocs.org/projects/trump/badge/?version=latest
   :target: https://readthedocs.org/projects/trump/?badge=latest
   :alt: Documentation Status

------------------------------------------
Persistent Objectification of Indexed Data
------------------------------------------

Trump is a framework for objectifying data, with the goal of centralizing the responsibility of 
managing feeds, munging, calculating and validating data, upstream of any application or user requirement.

With a focus on business processes, Trump's long run goals enable data feeds to be:

* **Prioritized**, *flexibly* - a symbol can be associated with multiple data source for a variety of reasons including redundancy, calculations, or optionality.
* **Modified**, *reliably* - a symbol's data feeds can be changed out, without any changes requiring testing to the downstream application or user.
* **Verified**, *systematically* - a variety of common data processing checks are performed as the symbol's data is cached.
* **Audited**, *quickly* - alerts and reports all become possible to assess integrity or inspect where manual over-rides have been performed.
* **Aggregated**, *intelligently* - on a symbol by symbol basis, feeds can be combined and used in an extensible number of ways.
* **Customized**, *dynamically* - extensibility is possible at the templating, munging, aggregation, and validity steps.

Planning
========

Trump is still in a planning stage.  Trump's initial priority is numeric and monotonic timeseries data,
but written with the future in mind to eventually work with any sortable object as data, and any object as an index.
Eliminating the monotonic assumption is a very low priority. 

See `docs/planning.md <https://github.com/Equitable/trump/blob/master/docs/planning.md>`_ for the current state of the project.

Basic Usage
===========
This example dramatically understates the utility of Trump's long term feature set.

Adding a Symbol
---------------

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import fQuandl, fGoogleFinance, fYahooFinance

   sm = SymbolManager()

   TSLA = sm.create(name = "TSLA", description = "Tesla Closing Price USD",
                   freq = 'B', units = '$ / share')

   TSLA.addTags(["stocks","US"])

   #Try Google First
   #If Google's feed has a problem, try Quandl's backup
   #If all else fails, use Yahoo's data...

   TSLA.addFeed(fGoogleFinance("TSLA"))                          
   TSLA.addFeed(fQuandl("GOOG/NASDAQ_TSLA",fieldname='Close'))
   TSLA.addFeed(fYahooFinance("TSLA"))

   #Optional munging, validity checks, tags, and aggregation settings are planned...
   
   #All three are cached...
   TSLA.cache()

   print TSLA.df.tail()

                 TSLA
   dateindex         
   2015-03-20  198.08
   2015-03-23  199.63
   2015-03-24  201.72
   2015-03-25  194.30
   2015-03-26  190.40 
   
   sm.finish()
   
Using a Symbol
--------------

.. code-block:: python

   from trump.orm import SymbolManager

   sm = SymbolManager()

   TSLA = sm.get("TSLA")

   #optional
   TSLA.cache()

   print TSLA.df.tail()
   
                 TSLA
   dateindex         
   2015-03-20  198.08
   2015-03-23  199.63
   2015-03-24  201.72
   2015-03-25  194.30
   2015-03-26  190.40  

   sm.finish()

   
Installation
============

See the latest `Installation instructions on ReadTheDocs.org <http://trump.readthedocs.org/en/latest/installation.html>`_

Requirements
------------
* Python 2.7; Support for Python 3.3 or 3.4 is do-able, if there is demand.
* PostgreSQL 9.4 (untested on previous versions) or potentially any relational database supported by SQLAlchemy (preliminary testing with SQLite3 on linux, indicates a bug associated with object type)

Dependencies
------------
- `Pandas <http://pandas.pydata.org/>`_ (Tested with >= 15.2)
- `SQLAlchemy <http://sqlalchemy.org/>`_ (Tested with >= 0.9)
- `Smuggle <https://pypi.python.org/pypi/smuggle>`_ (Tested with >= 0.2.0)

Data Source Dependencies
------------------------
- `Quandl <https://pypi.python.org/pypi/Quandl>`_

Documentation
=============
Read the latest on `ReadTheDocs.org <http://trump.readthedocs.org>`_

Communication
=============

* Questions, Bugs, Ideas & Requests -> GitHub Issues or InvTech@equitable.ca
* Contribute Code -> New Branch + GitHub Pull Request
* Chat -> `Gitter <https://gitter.im/Equitable/trump>`_

License
=======
BSD-3 clause.  See the actual `License <https://raw.githubusercontent.com/Equitable/trump/master/LICENSE.txt>`_.

Background
==========
The prototype for ``Trump`` was built at Equitable Life of Canada in 2014 by Jeffrey McLarty, CFA 
and Derek Vinke, CFA. 
