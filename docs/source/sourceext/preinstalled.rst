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



