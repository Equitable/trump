
Framework
---------

The pseudo code for a macro view of the main object model for trump is below.

The implementation is more extensive, but in general, trump is a system
to organize symbols, which are made up of one or more feeds to data sources.

There are template classes used to facilitate simpler instantiation 
and customization.

Below is for illustrative purposes of the short-term plan for Trump.  

.. code-block:: python

   class Feed(object):
      def __init__(self):
         self.symname = str
         self.fnum = int
         self.state = str # ON/OFF 
         self.ftype = str # Feed type
         
         self.tags = [str,]
         
         # This is a list of arguments and values that get
         # passed to whatever API is called out by meta's 'stype' key.
         self.sourcing = {str : str,...}                   # { param : value,}
         
         # This is a list any strings that need to be associated with this 
         # feed. Eg. 'stype'.
         self.meta = {str : str,...}                       # { attr : value,}
         
         #self.validity = {(str, str, str) : str,...}      # { (checkpoint, logic, key) : value,}    
         self.munging = {(int, str) : {str : str,...},...} # { (order, mtype, method) : {argument : value,},}
        
   class Symbol(object):
      def __init__(self):
         self.name = str
         self.description = str
         self.freq = str         
         self.units = str
         
         self.agg_method = str                      # PRIORITY, etc.
                                                    
         self.tags = [str,...]                      
         self.aliases = [str,...]                   
                                                    
         self.feeds = [(int, Feed),...]             # [ (fnum, Feed),]
                                                    
         self.validity = {(str, str, str) : str,...}# { (checkpoint, logic, key) : value,}
         
         self.datatable = Table(index,data,[Feed.data,Feed.data,...])
         
         self.feeddata = DataFrame(self.datatable)
         
         self.df = DataFrame(self.datatable)
         
         self.s = Series(self.datatable)

There are many improvements that can be made over and above this model.

The lowest hanging fruit would be to a) turn all values currently stored as 
a string, and turn it into (type, value)

Another logical improvement would be to turn the agg_method's str into { str : {str : str,...}...}