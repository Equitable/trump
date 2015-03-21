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

Step 2. Configuration
---------------------
Edit trump/config/trump.cfg

Populate the [readwrite] section with a SQLAlchemy engine string.

Step 3. Template Settings
-------------------------
Edit trump/templating/settings cfg files, depending on the intended data sources to be used.

Only Quandl and DBAPI are currently implemented.

See the documentation section "Configuring Data Sources" for guidance.

Step 4. Import Trump
--------------------
Running ``import trump.orm`` will create all the tables required in whatever database
was provided in Step 2.

If it all worked, you will see "Trump is ready."