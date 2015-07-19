Installation 
============

Step 1. Install Package
-----------------------

*SUMMARY OF STEP 1: Clone and install trump, from github.*

``git clone https://github.com/Equitable/trump.git``
+
``cd trump``
+
``python setup.py install``

.. note::

	If you use any other installation method (Eg. ``python setup.py develop``),  
	you will need to manually create your own .cfg files, in step 2, by renaming the 
	.cfg_sample files to cfg files.

.. note::

	Trump is setup to work with ``pip install trump``, however the codebase and features
	are being worked on very quickly right now (2015Q2).  The version on pypi, will be very stale, very
	quickly.  It's best to install from the latest commit to the master branch direct from GitHub.

Step 2. Configure Settings 
--------------------------

*SUMMARY OF STEP 2: Put a SQLAlchemy Engine String in trump/config/trump.cfg.  Comment out all other engines.*

Trump needs information about a database it can use, plus there are a couple other settings you
may want to tweak.  You can either follow the instructions below, or pass a
SQLAlchemy engine/engine-string, to both SetupTrump() and SymbolManager() everytime you use them.

The configuration file for trump is in:

userbase/PythonXY/site-packages/trump/config/trump.cfg

or

yourprojfolder/trump/config/trump.cfg

.. note::

	A sample config file is included, by the name trump.cfg_sample.  Depending on your installation
	method, you may need to copy and rename it to trump.cfg.  cfg files aren't tracked by git,
	nor does the installation do anything other than copy and rename the file extension.
	``pip`` and ``python setup.py install`` will rename them for you.
	``python setup.py develop`` won't rename them for you, you'll have to do it yourself.

Assuming you want to use a file based sqlite database (easiest, for beginners), change:

``engine: sqlite://`` to 
``;engine: sqlite://``  (notice the semi-colon, this just comments out the line)

and change this line:

``;engine: sqlite:////home/jnmclarty/Desktop/trump.db``  to

``engine: sqlite:////home/path/to/some/file/mytrumpfile.db`` (on linux) or

``engine: sqlite:///C:\path\to\some\mytrumpfile.db`` (on windows)

The folder needs to exist in advance, the file should not exist.  Trump creates the file.

Step 3. Adjust Existing Template Settings (Optional)
---------------------------------------------------

*SUMMARY OF STEP 3: Adjust any settings for templates you intend you use.*

Trump has template settings, stored in multiple settings files, using an identical method as the 
config file in Step 2.  ``pip`` or ``python setup.py install`` would have created some from samples.
Using any other installation methode, you would have to rename cfg_sample to cfg yourself.

The files are here:

userbase/PythonXY/site-packages/trump/templates/settings/

or

yourprojfolder/trump/templates/settings/

Edit trump/templating/settings cfg files, depending on the intended data sources to be used.

See the documentation section "Configuring Data Sources" for guidance.

Step 4. Run SetupTrump()
------------------------

*SUMMARY OF STEP 4: Run trump.SetupTrump(), to setup the tables required for Trump to work.*

Running the code block below, will create all the tables required in the database
provided in Step 2.

.. code-block:: python
	
	from trump import SetupTrump
	SetupTrump()
	# Or, if you skipped step 2 correctly, you could do:
	SetupTrump(r'sqlite:////home/path/to/some/file/mytrumpfile.db')

If it all worked, you will see "Trump is installed @...".   You're Done!  Hard part is over.

You're now ready to create a SymbolManager, which will help you create your first symbol.  

.. code-block:: python
	
	from trump import SymbolManager
	sm = SymbolManager()
	# Or, if you skipped step 2 correctly, you could do:
	sm = SymbolManager(r'sqlite:////home/path/to/some/file/mytrumpfile.db')
	...
	mysymbol = sm.create('MyFirstSymbol') # should run without error.

Configuring Data Sources
------------------------
Data feed source template classes map to their respective .cfg file in the templating/settings directory,
as discussed in Step 3.

The goal of the files is to add a small layer of security.  The goal of the template classes is to reduce code during
symbol creation scripts.  There is nothing preventing a password from being hardcoded into a template, the 
same way a tablename can be added to a .cfg file.  It's only a maintenance decision for the admin.

The sections of the cfg files get used by the template's in their respective classes.  The section of the config files'
names are then either referenced at the symbol creation point, storing .cfg file info with the symbol in the database,
or leaving Trump to query the attributes at every cache, from the source .cfg file.

Trump will use parameters for a source in the following order:

1. Specified explicitly when a template is used. (Eg. table name)

.. code-block:: python

   #Assuming the template doesn't clober the value.
   myfeed = QuandlFT(authtoken='XXXXXXXX') 
   
2. Specified implicitly using default value or logic derived in the template. (Eg. Database Names)

.. code-block:: python

   class QuandlFT(object):
      def __init__(authtoken ='XXXXXXXXX'):
         if len(authtoken) == 8:
            self.authtoken = authtoken
         else:
            self.authtoken = 'YYYYYYYYY'
           
3. Specified implicitly using read_settings(). (Eg. database host, port)

.. code-block:: python

   class QuandlFT(object):
      def __init__(**kwargs):
	     autht = read_settings('Quandl', 'userone', 'authtoken')
         self.authtoken = autht

4. Specified via cfg section. (Eg. authentication keys and passwords)

.. code-block:: python

   class QuandlFT(object):
      def __init__(**kwargs):
         self.meta['stype'] = 'Quandl' #cfg file name
         self.meta['sourcing_key'] = 'userone' #cfg file section
         
contents of templating/settings/Quandl.cfg:
         
.. code-block:: text

   [userone]
   authtoken = XXXXXXXXX

If the template points to a section of a config file, rather than reading in a value from a config file,
(ie, #4), the info will not be stored in the database.  Instead, the information will be looked up
during caching from the appropriate section in the cfg file.

This means that the cfg file values can be changed post symbol creation, outside of Trump.

Testing the Installation
------------------------

After Trump has been configured, and pointed at a database via an engine string using 
a config file, one can run the py.test enabled test suite.  The tests require network
access, but will skip certain tests without it.  The testing suite makes a mess, and doesn't clean
up after itself.  So, be prepared to run it on a database which can be delete immediately after.

Insight into compatibility with databases other SQLite and PostGres, are of interest to the maintainers.
So, if you run the test suite on some other database, and it all works, do let us know via a GitHub issue or e-mail.
If it doesn't, please let us know that as well!

Uninstall
=========

#. Delete all tables Trump created. (There is a script, which attempts to do that for you.  See uninstall.py.
This will (attempt to) remove all tables created by Trump. The file will likely require minor changes
if you use anything other than PostgreSQL, or if it hasn't been updated to reflect newer tables in Trump.)
#. Delete site-packages/trump and all it's subdirectories.