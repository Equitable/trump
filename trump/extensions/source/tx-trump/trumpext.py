"""
Required kwargs:

- 'symbolname'

Optional kwargs:

- 'enginestr' - SQLAlchemy engine string, pointing to a trump install.
- 'cache_first' - Bool
- 'croptime' - crop the time.

"""

stype = 'Trump'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        from trump import SymbolManager
        from trump.orm import ENGINE_STR
        if 'enginestr' in kwargs:
            engstr = kwargs['enginestr'] 
        engstr = engstr or ENGINE_STR
        self.sm = SymbolManager(engstr)
        #Todo Check to understand if this session is kept open or not.
    def getseries(self, ses, **kwargs):
        
        #TODO Test to see if ses could be used here.  Right now, this feels safer.
        sym = self.sm.get(kwargs['symbolname'])
        
        if 'cache_first' in kwargs:
            if kwargs['cache_first']:
                sym.cache()
        
        data = sym.df[kwargs['symbolname']]
        
        try:
            croptime = kwargs['croptime']
        except:
            croptime = False
        if croptime:
            data.index = [t.to_datetime().date() for t in data.index]

        return data