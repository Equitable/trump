Installation
============

Step 1. Install Package:
------------------------
``pip install trump``

or

``git clone https://github.com/Equitable/trump.git``
+
``python setup.py install``

If you use any other installation method (Eg. ``python setup.py develop``),  
you will need to manually create your own .cfg files by renaming the .cfg_sample files.

Step 2. Configure the Template Defaults 
---------------------------------------
Edit trump/config/trump.cfg

Populate the [readwrite] section with a SQLAlchemy engine string.

Step 3. Adjust Existing Template Settings
-----------------------------------------
Edit trump/templating/settings cfg files, depending on the intended data sources to be used.

See the documentation section "Configuring Data Sources" for guidance.

Step 4. Run SetupTrump()
------------------------
Running ``from trump import SetupTrump`` will create all the tables required in whatever database
was provided in Step 2.

If it all worked, you will see "Trump is installed @..."

Configuring Data Sources
========================
Data feed source template classes map to their respective .cfg file in the templating/settings directory.

The goal of the files is to add a small layer of security.  The goal of the template classes is to reduce code during
symbol creation scripts.  There is nothing preventing a password from being hardcoded into a template, the 
same way a tablename can be added to a .cfg file. 

The sections of the cfg files get used by the template's in their respective classes.  The section of the config files
names are then either referenced add the symbol creation point, storing .cfg file info with the symbol in the database,
or leaving Trump to query the attributes at every cache, from the the source .cfg file.

Trump will use parameters for a source in the following order:

1. Specified explicitly when a template is used. (Eg. table name)

.. code-block:: python

   myfeed = QuandlFT(authtoken='XXXXXXXX') #Assuming the template doesn't clober the value.
   
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
         self.authtoken = read_settings()['Quandl']['userone']['authtoken']

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

5. Specified on disk encrypted sources via an encrypted config file. (Eg. top-secret passwords)

Same as #4, but using an encrypted file.  Not implemented yet.

If the template and settings rely on #4 (or hypothetical #5), the info will not be stored in the database.
Instead, it will be looked up during caching from the appropriate section in the cfg file.
This means that the cfg file values can be changed post symbol creation, but the specific arguments can
not be modified.

Uninstall
=========

1. Download uninstall.py, and run it.  This will remove all tables created by Trump. The file will likely require minor changes if you use anything other than PostgreSQL.

2. Delete site-packages/trump and all it's subdirectories.

That's it.