Creating & Modifying Source Extensions
======================================

This section of the docs is really only intended for those who want to write, or modify,
their own source extensions.  But, it can be helpful to understand how they work, even for those who
don't want to write an extension.

Trump's framework enables sources of varying, dynamic, and proprietary types.  A source extension is
basically a generalized way of getting a pandas Series out of an existing external API. For instance
examples include, the pandas datareader, a standardized DBAPI 2.0 accessible schema, a proprietary
library, or something as simple as a CSV file.  At a high level, each symbol's feed's source's kwargs
are passed to the appropriate source extension, based on the defined source type.

When each symbol is cached, it loops through each of it's feeds.  Each feed's source is queried,
using four critical python lines in orm.Feed.cache():

.. code-block:: python

   if stype in sources:
      self.data = sources[stype](self.ses, **kwargs)        
   else:
      raise Exception("Unknown Source Type : {}".format(stype))

The important line, is the second one.  'sources', is a dictionary loaded every time trump's orm.py is 
imported.  The key's are just strings representing the "Source Type", 
eg. "DBAPI", "Quandl", "BBFetch" (Example of a proprietary source).
The values of the sources dictionary are SourceExtension objects.  The SourceExtension objects wrap modules discovered 
dynamically when loader.py scans the source extension folder.  The code for the SourceExtension
is below:

.. code-block:: python

   class SourceExtension(object):
      def __init__(self, mod):  #instantiated only once per import of trump.orm
         self.initialized = False
         self.mod = mod
         self.renew = mod.renew
         self.Source = mod.Source
      def __call__(self, _ses, **kwargs):  #called each symbol's feed's cache (in the second line above)
         if not self.initialized or self.renew: 
            self.fetcher = self.Source(_ses, **kwargs)
            self.initialized = True
         return self.fetcher.getseries(_ses, **kwargs)

A SourceExtension is instantiated only once, when loader.py passes a module it discovered.  
The modules, are the "source extension", which are just simply python files, required to be created in a 
standard way.  The standard can be illustrated with an example.  Below, is an example csv-file 
source extension (which may be stale, compared to the actual csv extension).

See trump/extensions/source for more examples.  

.. code-block:: python

   stype = 'PyDataCSV'
   renew = False

   class Source(object):
      def __init__(self, ses, **kwargs):
         from pandas import read_csv
         self.read_csv = read_csv

      def getseries(self, ses, **kwargs):
      
         col = kwargs['data_column']
         del kwargs['data_column']
         
         fpob = kwargs['filepath_or_buffer']
         del kwargs['filepath_or_buffer']
         
         df = self.read_csv(fpob, **kwargs)
         
         data = df[col]

         return data

Noticed that the two variables, stype & renew, as well as the Source class, are used in the SourceExtension
instantiation.

Source Extension Standard Form
------------------------------

Any extension module needs 3 things; an stype variable, renew variable, and Source class.

stype (str)
^^^^^^^^^^^

stype is the string used in the 'sources' dictionary mentioned earlier, and must match the
the stype set in the corresponding Source template(s).

renew (boolean)
^^^^^^^^^^^^^^^

renew is a boolean, which determines if the Source object is reinstantiated on 
every use.  For instance, one might create a source, which sets up a database connection, which
stays open for the life of any script using trump's orm, but only if that specific source
is used at least once.  Renew would be set to False,
and the connection logic, would be put in Source.__init__.  Alternatively, if a new connection would
be required on every symbol's cache, renew would be set to True.  The tradeoffs, are speed and 
resource constraints. Both __init__ and getseries get the same arguments.  The current live 
trump session, and the symbol's feed's source kwargs.

Source (class)
^^^^^^^^^^^^^^

Source is an an object with one other method, getseries, other than the constructor (__init__).
Both take the same arguments: the trump session, and the Symbol's Feed's Source's kwargs.  getseries,
returns a dataframe.

.. This page is auto generated via trump/extensions/document.py
.. Editing it, is silly, as it will be overwritten.  The docstring
.. of the modules should themselves be edited.

Pre-Installed Source Extensions
===============================

BBFetch
-------
.. code-block:: python

   # the directory is tx-bbfetch
   stype = 'BBFetch'
   renew = True

Required kwargs:

- 'elid' 
- 'bbtype' = ['COMMON', 'BULK'], then a few relevant kwargs depending on each.

Optional kwargs:

- 'duphandler' - 'sum'
- 'croptime' - boolean



DBAPI
-----
.. code-block:: python

   # the directory is tx-dbapi
   stype = 'DBAPI'
   renew = True

The DBAPI driver, will use by default the same driver SQLAlchemy is using for trump. 
There is currently no way to change this default.  It's assumed that the driver
is DBAPI 2.0 compliant.

Required kwargs include:

- 'dbinsttype' which must be one of 'COMMAND', 'KEYCOL', 'TWOKEYCOL'
- 'dsn', 'user', 'password', 'host', 'database', 'port'

Optional kwargs include:

- duphandler ['sum'] which just groups duplicate index values together via the sum.

Additional kwargs:

Required based on 'dbinsttype' chosen:

'COMMAND' : 
- 'command' which is just a SQL string, where the first column becomes the index, and the second
column becomes the data.

'KEYCOL' :
- ['indexcol', 'datacol', 'table', 'keycol', 'key']

'TWOKEYCOL' :
- ['indexcol', 'datacol', 'table', 'keyacol', 'keya', 'keybcol', 'keyb']



psycopg2
--------
.. code-block:: python

   # the directory is tx-psycopg2
   stype = 'psycopg2'
   renew = True

Started extension for a Postgres-specifc source.

Not fully implemented.



PyDataCSV
---------
.. code-block:: python

   # the directory is tx-pydatacsv
   stype = 'PyDataCSV'
   renew = False

All kwargs are passed to panda's read_csv function.

Additional required kwargs:

- 'filepath_or_buffer' - should be an absolute path.  Relative will only work, if caching is only
performed by a python script which can access the relative path.

- 'data_column' - the specific column required, so to turn the dataframe into a series.


PyDataDataReaderST
------------------
.. code-block:: python

   # the directory is tx-pydatadatareaderst
   stype = 'PyDataDataReaderST'
   renew = True

This uses pandas.io.data.DataReader, all kwargs get passed to that.

start and end are optional, but must be of the form 'YYYY-MM-DD'.

Will default to since the beginning of available data, and run through "today".

data_column is required to be specified as well.



Quandl
------
.. code-block:: python

   # the directory is tx-quandl
   stype = 'Quandl'
   renew = True

All kwargs are passed to Quandl's API quandl.get()

An additional 'fieldname' is available to select a specific column if a specifc quandl DB,
doesn't support quandl's version of the same feature.



SQLAlchemy
----------
.. code-block:: python

   # the directory is tx-sqlalchemy
   stype = 'SQLAlchemy'
   renew = True

a SQLAlchemy based implementation...so an engine string could be used.

Not fully implemented


WorldBankST
-----------
.. code-block:: python

   # the directory is tx-worldbankst
   stype = 'WorldBankST'
   renew = False

Uses pandas.io.wb.download to query indicators, for a specific country.

country, must be a world bank country code.

Some assumptions as implied about the indicator and the first level of the index.  This 
may not work for all worldbank indicators.



