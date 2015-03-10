# -*- coding: utf-8 -*-
"""
Trump's templating system consists of pure-python objects, which can
be converted into either lists, dictionaries, or ordered dictionaries,
which can then be used in the generalized constructors of Trump's SQLAlchemy 
based ORM system.
"""

from collections import OrderedDict as odict, 

from bases import  bTags, bMunging, bSource, bFeed

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

class mFFill(tMunging):
    def __init__(self,method='ffill'):
        super(mFFill, self).__init__()       
        self.build_ffillna(method=method)

class mAddFFillMult(tMunging):
    def __init__(self,add=0.0,method='ffill',mult=1.0):
        super(mAddFFillMult, self).__init__()
        self.build_ffillna(method=method)
        self.build_add_const(add)
        self.build_mult_const(mult)
        
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

class sDBAPI2Connection(bSource):
    def __init__(self,dsn=None,user=None,password=None,host=None,database=None):
        super(sDBAPI2Connection,self).__init__()
        self.set_LocalDB(dsn,user,password,host,database)
        self.set_basic()
        return None
            
class sSQLAlchemySession(bSource):
    def __init__(self,enginestr):
        super(sSQLAlchemySession,self).__init__()
        self.enginestr = enginestr
        self.set_basic()
        return None
               
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

class fDBAPI2(bFeed):
    def __init__(self,table=None,dsn=None,user=None,password=None,host=None,database=None):
        super(fDBAPI2, self).__init__()
        if self.ftype == 'DBAPI2':
            s = sDBAPI2Connection(dsn,user,password,host,database)
            s.set_basic(table)
            self.sourcing = s.as_dict            

class fEcon(fDBAPI2):
    def __init__(self,key):
        super(fEcon, self).__init__()
        s = sDBAPI2Connection()
        s.set_LocalDB('General')
        s.set_keycol('econ','name',key,'date','value')
        self.sourcing = s.as_dict

class fSQLAlchemy(bFeed):
    def __init__(self,enginestr,table):
        super(fSQLAlchemy, self).__init__()
        s = sSQLAlchemySession(enginestr)
        s.set_basic(table)
        self.sourcing = s.as_dict
        
class fQuandl(bFeed):
    def __init__(self,dataset,**kwargs):
        super(fQuandl, self).__init__()
        tmp = {'dataset' : dataset, 'authtoken' : QuandlAPIkey}
        self.sourcing = dict(tmp.items() + kwargs.items())