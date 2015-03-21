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

* Prioritized, flexibly - a symbol can be associated with multiple data source for a variety of reasons including redundancy, calculations, or optionality.
* Modified, reliably - a symbol's data feeds can be changed out, without any changes requiring testing to the downstream application or user.
* Verified, systematically - a variety of common data processing checks are performed as the symbol's data is cached.
* Audited, quickly - alerts and reports all become possible to assess integrity or inspect where manual over-rides have been performed.
* Aggregated, intelligently - on a symbol by symbol basis, feeds can be combined and used in an extensible number of ways.
* Customized, dynamically - extensibility is possible at the templating, munging, aggregation, and validity steps.

Planning
========

Trump is still in a planning stage.  Trump's initial priority is numeric and monotonic timeseries data,
but written with the future in mind to eventually work with any sortable object as data, and any object as an index.
Eliminating the monotonic assumption is a very low priority. 

See doc/planning.md for the current state of the project.

Basic Usage
===========
Coming soon.

Installation
============

See the latest on `readthedocs <trump.readthedocs.org>`_

Requirements
------------
* Python 2.7; Support for Python 3.3 or 3.4 is do-able, if there is demand.
* A relational database supported by SQLAlchemy.  The first database with guaranteed support is PostGreSQL.

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
Read the latest on `readthedocs <trump.readthedocs.org>`_

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
