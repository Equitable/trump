# -*- coding: utf-8 -*-
"""
Trump's templating system consists of pure-python objects, which can
be converted into either lists, dictionaries, or ordered dictionaries,
which can then be used in the generalized constructors of Trump's SQLAlchemy 
based ORM system.
"""

from bases import  bTags, bMunging, bSource, bFeed

from trump.options import read_settings

"""
*******************************************************************************
*
*  Tag Templates
*
* Tag Templates are any object which implements a property called 
* as_list, which returns a list of strings
*
*******************************************************************************
"""

class tAsset(bTags):
    def __init__(self,cls):
        if cls.lower() in ('equity','stock','equities','stocks'):
            self.equity = True
        elif cls.lower() in ('bond','bonds'):
            self.bond = True
        elif cls.lower() in ('pref','prefferred','preferred','prefered'):
            self.pref = True
        elif cls.lower() in ('comodity','commodity','commodities'):
            self.commodity = True

class tGeneric(bTags):
    def __init__(self,tags):
        for t in tags:
            self.__setattr__(self,t,True)
        
class tSimple(bTags):
    def __init__(self,tags):
        self.tags = tags
    def as_list(self):
        return self.tags
        
"""
*******************************************************************************
*
*  Munging Templates
*
* Munging Templates are any object which implements a property called 
* as_odict, which returns an odict where each key is a function in 
* munging_methods, and it's value is an object which represents the parameters
* to use on that object.  This should be sufficient to pass to a 
* a Feed constructor's munging parameter, which then becomes FeedMungingArgs objects
* making up a FeedMunge object, of which will be the instructions associated
* with a specific Feed object.
*
*******************************************************************************
"""

from munging_helpers import mixin_pab, mixin_pnab

class mAbs(bMunging, mixin_pab):
    def __init__(self):
        super(mAbs, self).__init__()       
        self.bld_abs()

class mRollingMean(bMunging, mixin_pnab):
    def __init__(self,**kwargs):
        super(mRollingMean, self).__init__()       
        self.bld_rolling_mean(**kwargs)

class mFFillRollingMean(bMunging, mixin_pab, mixin_pnab):
    def __init__(self,**kwargs):
        super(mFFillRollingMean, self).__init__()   
        self._bld_pab_generic('ffill')
        self.bld_rolling_mean(**kwargs)

class mRollingMeanFFill(bMunging, mixin_pab, mixin_pnab):
    def __init__(self,**kwargs):
        super(mFFillRollingMean, self).__init__()   
        self.bld_rolling_mean(**kwargs)
        self._bld_pab_generic('ffill')

class mMultiExample(bMunging, mixin_pnab, mixin_pab):
    def __init__(self,pct_change_kwargs,add_kwargs):
        super(mMultiExample, self).__init__()       
        self.bld_pct_change(**pct_change_kwargs)        
        self.bld_add(**add_kwargs)  

class mSimpleExample(bMunging, mixin_pnab, mixin_pab):
    def __init__(self,periods,window):
        super(mSimpleExample, self).__init__()
        kwargs = {'periods' : periods, 'fill_method' : 'ffill'}
        self.bld_pct_change(**kwargs)
        kwargs = {'window' : window, 'min_periods' : 5}
        self.bld_rolling_mean(**kwargs)      
       
"""
*******************************************************************************
* 
*  Source Templates
*
* Source Templates are any object which implements a property called
* as_dict.  The keywords and values of which are sufficient to pass to a 
* a Feed constructor's source parameter, which then become FeedSource objects
* making up a source.
*
*******************************************************************************
"""

from source_helpers import mixin_dbCon, mixin_dbIns

class sDBAPI(bSource, mixin_dbCon, mixin_dbIns):
    def __init__(self,dsn=None,user=None,password=None,host=None,database=None,sourcing_key=None):
        super(sDBAPI,self).__init__()
        self.set_con_params(dsn,user,password,host,database,sourcing_key)
            
class sSQLAlchemySession(bSource):
    def __init__(self,enginestr):
        super(sSQLAlchemySession,self).__init__()
        self.enginestr = enginestr
        self.set_basic()
               
"""
*******************************************************************************
* 
*  Feed Templates
*
* These objects need an tags, sourcing, munging and validity attribute
* defined.  They must be a list, dict, odict, and dict, respectively.
*
*******************************************************************************
"""

skey = 'explicit'

class fDBAPI(bFeed):
    def __init__(self,table=None,indexcol=None,datacol=None,dsn=None,user=None,password=None,host=None,database=None,sourcing_key=None):
        super(fDBAPI, self).__init__()
        self.set_stype()
        if sourcing_key:
            self.set_sourcing_key(sourcing_key)
        self.s = sDBAPI(dsn,user,password,host,database,sourcing_key)
        if self.__class__.__name__ == 'fDBAPI':
            self.s.set_basic(table,indexcol,datacol)
            self.sourcing = self.s.as_dict
    def set_stype(self):
        self.meta['stype'] = 'DBAPI'
    def set_sourcing_key(self,sourcing_key):
        self.meta['sourcing_key'] = sourcing_key

class fExplicitKeyCol(fDBAPI):
    def __init__(self,table,keycol,key,indexcol,datacol):
        super(fExplicitKeyCol, self).__init__(sourcing_key=skey)
        self.s.set_keycol(table,keycol,key,indexcol,datacol)
        self.sourcing = self.s.as_dict
       
class fExplicitBasic(fDBAPI):
    def __init__(self,table,datacol,indexcol):
        super(fExplicitBasic, self).__init__(table=table,
                                             indexcol=indexcol,
                                             datacol=datacol,
                                             sourcing_key=skey)
        self.s.set_basic(table,indexcol,datacol)
        self.sourcing = self.s.as_dict

class fExplicitCommand(fDBAPI):
    def __init__(self,command):
        super(fExplicitCommand, self).__init__(sourcing_key=skey)
        self.s.set_command(command)
        self.sourcing = self.s.as_dict

class fEcon(fExplicitKeyCol):
    def __init__(self,key):
        super(fEcon,self).__init__('econ','name',key,'date','value')

class fMyTable(fExplicitBasic):
    def __init__(self,table,datacol='value',indexcol='date'):
        super(fMyTable,self).__init__(table,datacol,indexcol)
        
class fSQL(fExplicitCommand):
    pass
        
class fSQLAlchemy(bFeed):
    def __init__(self,enginestr,table):
        super(fSQLAlchemy, self).__init__()
        s = sSQLAlchemySession(enginestr)
        s.set_basic(table)
        self.sourcing = s.as_dict

#******************************************************************************
#
#   Quandl
#
#******************************************************************************

class fQuandl(bFeed):
    def __init__(self,dataset,**kwargs):
        super(fQuandl, self).__init__()
        QuandlAPIkey = read_settings()['Quandl']['userone']['authtoken']
        tmp = {'dataset' : dataset, 'authtoken' : QuandlAPIkey}
        self.sourcing = dict(tmp.items() + kwargs.items())    
        self.set_stype()
    def set_stype(self):
        self.meta['stype'] = 'Quandl'

class fQuandlSecure(fQuandl):
    def __init__(self,dataset,**kwargs):
        super(fQuandl, self).__init__()
        tmp = {'dataset' : dataset }
        self.sourcing = dict(tmp.items() + kwargs.items())
        self.set_stype()
        self.meta['sourcing_key'] = 'userone'

if __name__ == '__main__':
    f = fMyTable('atable')
    print f.sourcing
    print f.meta
    
    f = fEcon('SP500')
    print f.sourcing
    print f.meta
    
    f = fSQL('SELECT t,data FROM math ORDER BY t;')
    print f.sourcing
    print f.meta

    m = mRollingMean(window=5,min_periods=4,center=True)
    for key in m.as_odict.keys():
        print key
        for ins in m.as_odict[key]:
            print " ", m.as_odict[key][ins]

    m = mSimpleExample(3,5)
    for key in m.as_odict.keys():
        print key
        for ins in m.as_odict[key]:
            print " ", m.as_odict[key][ins]