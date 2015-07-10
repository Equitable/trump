=====
Trump
=====

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/Equitable/trump
   :target: https://gitter.im/Equitable/trump?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://readthedocs.org/projects/trump/badge/?version=latest
   :target: https://readthedocs.org/projects/trump/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/Equitable/trump.svg
   :target: http://travis-ci.org/Equitable/trump/builds
   :alt: Travis CI Status

.. image:: https://coveralls.io/repos/Equitable/trump/badge.svg 
   :target: https://coveralls.io/r/Equitable/trump
   :alt: Coveralls.io
   
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

See `docs/planning.md <https://github.com/Equitable/trump/blob/master/docs/planning.md>`_ for the direction of the project.

Basic Usage
===========
This example dramatically understates the utility of Trump's long term feature set.

Adding a Symbol
---------------

.. code-block:: python

   from trump.orm import SymbolManager
   from trump.templating import QuandlFT, GoogleFinanceFT, YahooFinanceFT

   sm = SymbolManager()

   TSLA = sm.create(name = "TSLA", 
                    description = "Tesla Closing Price USD")

   TSLA.add_tags(["stocks","US"])

   #Try Google First
   #If Google's feed has a problem, try Quandl's backup
   #If all else fails, use Yahoo's data...

   TSLA.add_feed(GoogleFinanceFT("TSLA"))
   TSLA.add_feed(QuandlFT("GOOG/NASDAQ_TSLA",fieldname='Close'))
   TSLA.add_feed(YahooFinanceFT("TSLA"))

   #Optional munging, validity checks and aggregation settings would be
   #implemented here...
   
   #All three feeds are cached...
   TSLA.cache()

   #But only a clean version of the data is served up...
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

Contributing
============

If you're interested in contributing to Trump, we would love for you to do so!  The best place to
start is cloning the project, then use the latest commit from the master branch to install the package.
After that, follow the configuration instructions, in the installation instructions linked below.
While you do so, please make notes about any unclear parts or errors you get, during the
installation instructions. Please post an issue on GitHub with **ANY** notes, or if you're ambitious,
feel free to submit a pull request yourself.  Don't hesitate, doing either.

If it's not working, or unclear, it's our fault.  And, we really want it to be easy for people to
get started. It's really hard for the creator of the project, to assess their own instructions.

After installation, there are many paths to take; each one can be addressed by posting an issue,
or a pull request.  Exploring the docs, you'll inevitably find areas that need improving. Explore
the open issues, ones tagged with "Good First Pull Request" are the low hanging fruit.  Often,
current issues won't have a ton of information.  If you want to work on one, just add a comment,
asking for more info and mention that you're going to try to tackle it.  Also, just posting an
issue to "Say Hi", and ask for recommended issues to start on, is a great way to get started too.
   
Installation
============

See the latest `Installation instructions on ReadTheDocs.org <http://trump.readthedocs.org/en/latest/install.html>`_

Requirements
------------
* Python 2.7; Support for Python 3.3 or 3.4 is do-able, if there is demand.
* A Relational Database Supported by SQLAlchemy should work, however the following is tested:
  * PostgreSQL 9.4
  * Persistent SQLite (ie, file-based).  Certain features of Trump, wouldn't make sense with an in-memory implementation)

Dependencies
------------
- `Pandas <http://pandas.pydata.org/>`_ (Tested with >= 0.16.2)
- `SQLAlchemy <http://sqlalchemy.org/>`_ (Tested with >= 0.9)
- `smuggle <https://pypi.python.org/pypi/smuggle>`_ (Tested with >= 0.2.0)
- `validada <https://pypi.python.org/pypi/validada>`_ (Tested with >= 0.0.1)

Data Source Dependencies
------------------------
- `Quandl <https://pypi.python.org/pypi/Quandl>`_

Documentation
=============
Read the latest on `ReadTheDocs.org <http://trump.readthedocs.org>`_

Communication
=============

* Questions, Bugs, Ideas, Requests or just say "Hi" -> GitHub Issues, InvTech@equitable.ca, or jeffrey.mclarty@gmail.com
* Contribute Code -> New Branch + GitHub Pull Request
* Chat -> `Gitter <https://gitter.im/Equitable/trump>`_

License
=======
BSD-3 clause.  See the actual `License <https://raw.githubusercontent.com/Equitable/trump/master/LICENSE.txt>`_.

Background
==========
The prototype for ``Trump`` was built at Equitable Life of Canada in 2014 by Jeffrey McLarty, CFA 
and Derek Vinke, CFA. Jeffrey McLarty currently leads the Open Source initiative.
