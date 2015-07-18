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

stype
-----

stype is the string used in the 'sources' dictionary mentioned earlier, and must match the
the stype set in the corresponding Source template(s).

renew
-----

renew is a boolean, which determines if the Source object is reinstantiated on 
every use.  For instance, one might create a source, which sets up a database connection, which
stays open for the life of any script using trump's orm, but only if that specific source
is used at least once.  Renew would be set to False,
and the connection logic, would be put in Source.__init__.  Alternatively, if a new connection would
be required on every symbol's cache, renew would be set to True.  The tradeoffs, are speed and 
resource constraints. Both __init__ and getseries get the same arguments.  The current live 
trump session, and the symbol's feed's source kwargs.