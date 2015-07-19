=====
Trump
=====

************
Introduction
************

Trump is a framework for objectifying data, with the goal of centralizing the management
of data feeds to enable quicker deployment of analytics, applications, 
and reporting.  Munging data, common calculations, validation of data, can all be handled by Trump, upstream of 
any application or user requirement.

Inside the Trump framework, a symbol refers to one or more data feeds, each with their own instructions
saved for retrieving data from a specific source.  Once it's retrieved by Trump, depending on the attributes of the symbol,
it gets munged, aggregated, checked, and cached.  Downstream users are free to query the existing cache,
force a re-cache, or check any property of the data prior to using it.
 
System Admins can systematically detect problems in advance, via common integrity checks of the data,
then optionally schedule the re-cache by tag or symbol name.  Users and admins have the ability to manually
override problems if they exist, with a specific feed, in a way that is centralized, auditable, and backed-up efficiently.

With a focus on business processes, Trump's long run goals enable data feeds to be:

* **Prioritized**, *flexibly* - a symbol can be associated with multiple data source for a variety of reasons including redundancy, calculations, or optionality.
* **Modified**, *reliably* - a symbol's data feeds can be changed out, without any changes requiring testing to the downstream application or user.
* **Verified**, *systematically* - a variety of common data processing checks are performed as the symbol's data is cached.
* **Audited**, *quickly* - alerts and reports all become possible to assess integrity or inspect where manual over-rides have been performed.
* **Aggregated**, *intelligently* - on a symbol by symbol basis, feeds can be combined and used in an extensible number of ways.
* **Customized**, *dynamically* - extensibility is possible at the templating, munging, aggregation, and validity steps.

***************
Getting Started
***************

.. toctree::
   :maxdepth: 2
   :glob:
   
   install
   usage

************
Object Model
************

.. toctree::
   :maxdepth: 4

   objectmodel/orm
   dataflow
   aggregation

**********
Templating
**********

.. toctree::
   :maxdepth: 4
   
   templating/templates

*****************
Source Extensions
*****************

.. toctree::
   :maxdepth: 4
   
   sourceext

**************
User Interface
**************

.. toctree::
   :maxdepth: 2

   ui/ui