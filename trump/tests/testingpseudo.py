
###############################################################################
#
# Testing Core Functionality on a variety of database flavours and versions.
#  
#  Set it up, so that one could install PostGres 9.1, 9.2, 9.3, 9.4
#  SQLlite, and say one other eg. MySQL, and run them when the core team 
#  needs to, but not by default or when something like travis kicks off.
#
#  Likely a config file that matches some command line arguments...
#  how to make that work, maximizing DRY-like code, using pytest right off the bat.
#  Maybe ArgParse?
#  
###############################################################################

# for every database platform that we choose to support... [Postgresql, SQLite,... ]

   #if that database is available on this system AND the config file contains settings for it
   
       #for certain feed templates we create...  (Eg. Quandl)
       
           #test creating a symbol
       
           #caching a symbol
       
           #destroying a symbol

###############################################################################
#
# Testing Core SQLAlchemy Objects
#  
#  Being new to SQLAlchemy, and ORM in general, it would be great to 
#  generalize the checks to ensure that the core SQLAlchemy objects work.
#
#
#  The tricky part is that the objects can get instantiated
#  and modified, inside SQLAlchemy's session, but we need to check that the
#  same objects got created in the database, through another mechanism.
#  ...but, doing it in a way that is database agnotic.  Or, if that's not
#  possible, maybe create these tests in a way that they are set up
#  to switch certain parts of the test, depending on databases?
#
#  Or, maybe a new SQLAlchemy session, or engine, for each test?
#
###############################################################################

# for every method in the Symbol, Feed, SymbolCacher objects,

   # test that it works


###############################################################################
#
# Testing Templates
#  
#  These are all just pure python objects that need to check their attributes
#  existence.
#
#  The tricky part is they don't necessarily have to inherit from a certain
#  base class to be functional templates. 
#
#  So, if there's a way to re-organize the trump package,
#  so that new templates get tested without needing to touch
#  the test, that would be wicked.
#
###############################################################################

# for every feed template we create...
 
   # test it's constructor
 
   # test that it has all appropriate attributes after instantiation
 
  
# for every tag template we create...
    
    # test it's constructor
    
    # test that it's as_list() function works
    

# for every munging template we create...
    
    # test it's constructor
    
    # test that it's as_odict() function works
    

# for every validity template we create... #(Note Not implemented yet)

   # test it's constructor

   # test that it's as_dict() function works

###############################################################################
#
#  Aggregation functions
#
#  This part is fairly straight forward, it's just testing a bunch of functions
#
#  Bonus would be that if a basic set of tests could test all,
#  then one-offs could get their own test.
#  
###############################################################################

#  For every function in symbol_aggs's aggregation function builders,
  
  #  Test that they work as expected

