# -*- coding: utf-8 -*-
"""
Created on Sat Jan 03 21:02:02 2015

@author: Jeffrey
"""

from options import QuandlAPIkey

from collections import OrderedDict as odict

class _ListConverter(object):
    """
    any custom object that implements attributes which only store boolean
    values, and therefore can be converted into a list by inspecting it's
    attributes and values.
    """
    @property
    def as_list(self):
        if hasattr(self,'cust_list'):
            return self.cust_list
        class_builtins = set(dir(self.__class__))
        return [a for a in dir(self) if a not in class_builtins and getattr(self,a)]
        
class _DictConverter(object):
    """
    any custom object that can be converted into a dictionary by inspecting it's
    attributes and values.
    """
    @property
    def as_dict(self):
        if hasattr(self,'cust_dict'):
            return self.cust_dict
        if hasattr(self,'table'):
            if self.table == 'UNSPECIFIEDTABLE':
                raise Exception("Unspecified table in tFeed-like object's sourcing argument.")
        class_builtins = set(dir(self.__class__))
        return {a : getattr(self,a) for a in dir(self) if a not in class_builtins}
        
class _OrderedDictConverter(object):
    def __init__(self):
        self.attrorder = []
    @property
    def as_odict(self):
        if hasattr(self,'cust_odict'):
            return self.cust_odict
        od = odict()
        for attr in self.attrorder:
            od[attr] = getattr(self,attr)
        return od
    def __setattr__(self, name, value):
        self.__dict__[name] = value 
        if name != 'attrorder':
            self.attrorder.append(name)

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

class tTags(_ListConverter):
    def __init__(self):
        self.aTag = True
        self.bTag = True
        self.cTag = False
        self.dTag = True
        
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

class tMunging(_OrderedDictConverter):
    def build_add_const(self,n):
        self.add_const = {'n' : n}
    def build_mult_const(self,n):
        self.multiply_const = {'n' : n}
    def build_ffillna(self,**kwargs):
        self.ffillna = kwargs

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
class mixin_dbCon(object):
    def set_SoftCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):        
        """Derive the parameters right in the python file..."""
        self.dbcontype = "PARAM"
        self.dsn = '' #TODO Create for example purposes
        self.user = '' #TODO Create for example purposes
        self.password = '' #TODO Create for example purposes
        self.host = '' #TODO Create for example purposes
        self.database = '' #TODO Create for example purposes 
    def set_HardCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):
        """Store the parameters right in the python file..."""
        self.dbcontype = "PARAM"
        self.dsn = '' #TODO Create for example purposes
        self.user = '' #TODO Create for example purposes
        self.password = '' #TODO Create for example purposes
        self.host = '' #TODO Create for example purposes
        self.database = '' #TODO Create for example purposes 
    def set_LocalDB(self,dsn=None,user=None,password=None,host=None,database=None):           
        self.dbcontype = "PARAM"
        self.dsn = dsn or '' #TODO Read from config file
        self.user = user or '' #TODO Read from config file
        self.password = password or '' #TODO Read from config file
        self.host = host or '' #TODO Read from config file
        self.database = database or '' #TODO Read from config file
        
class mixin_dbIns(object):
    def set_keycol(self,table,keycol,key,datecol='date',valuecol='value'):
        self.dbinstype = "KEYCOL"
        self.table = table
        self.keycol = keycol
        self.key = key
        self.datecol = datecol
        self.valuecol = valuecol
        return self
    def set_basic(self,table=None,datecol='date',valuecol='value'):
        self.dbinstype = "BASIC"
        self.table = table or 'UNSPECIFIEDTABLE'
        self.datecol = datecol
        self.valuecol = valuecol
        return self
    def set_revbasic(self,table,revdatecol,datecol='date',valuecol='value'):
        self.dbinstype = "REVBASIC"
        self.table = table
        self.revdatecol = revdatecol
        self.datecol = datecol
        self.valuecol = valuecol
        return self
        
class tSource(_DictConverter, mixin_dbCon, mixin_dbIns):
    def __init__(self):
        self.stype = self.__class__.__name__

class sDBAPI2Connection(tSource):
    def __init__(self,dsn=None,user=None,password=None,host=None,database=None):
        super(sDBAPI2Connection,self).__init__()
        self.set_LocalDB(dsn,user,password,host,database)
        self.set_basic()
        return None
            
class sSQLAlchemySession(tSource):
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

class tFeed(object):
    def __init__(self):
        self.ftype = self.__class__.__name__
        self.tags = []
        self.sourcing = {}
        self.munging = odict()
        self.validity = {}
    def addTagTemplate(self,t):
        self.tags.append(t)
    def addSourceTemplate(self,k,v):
        self.sourcing[k] = v
    def addMungeTemplate(self,m,d=None,first=True):
        if hasattr(m,'as_odict'):
            print m.as_odict
            for k,v in m.as_odict.items():
                print k
                print v
                self.addMungeTemplate(k,v,True)
        else:
            if m not in self.munging:
                self.munging[m] = {}
            
            if isinstance(d,tuple) and first:
                for elem in d:
                    self.addMungeTemplate(m,elem,False)
            elif isinstance(d,dict) and first:
                for k in d:
                    self.munging[m][k] = str(d[k])
            elif any(isinstance(d,t) for t in (str,unicode,int,list,dict)):
                i = len(self.munging[m])
                self.munging[m]['arg' + str(i)] = str(d)
            else:
                raise Exception("Coulding add Munging {}, {}, {}".format(m,d,first))
    def addValidityTemplate(self,k,v):
        self.validity[k] = v
    def setTags(self,t):
        if any([isinstance(t,ty) for ty in (str,unicode)]):
            self.tags = [t]
        elif any([isinstance(t,ty) for ty in (list)]):
            self.tags = t
        return self
    def setSourcing(self,s):
        if any([isinstance(s,ty) for ty in (dict)]):
            self.sourcing = s
        else:
            raise Exception("Coudn't set source {}".format(s))
        return self
    def setMunging(self,m):
        if any([isinstance(m,ty) for ty in (odict)]):
            self.munging = m
        else:
            raise Exception("Coudn't set munging {}".format(m))
        return self
    def setValidity(self,v):
        if any([isinstance(v,ty) for ty in (dict)]):
            self.validity = v
        else:
            raise Exception("Coudn't set validity {}".format(v))
        return self

class fDBAPI2(tFeed):
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

class fSQLAlchemy(tFeed):
    def __init__(self,enginestr,table):
        super(fSQLAlchemy, self).__init__()
        s = sSQLAlchemySession(enginestr)
        s.set_basic(table)
        self.sourcing = s.as_dict
        
class fQuandl(tFeed):
    def __init__(self,dataset,**kwargs):
        super(fQuandl, self).__init__()
        tmp = {'dataset' : dataset, 'authtoken' : QuandlAPIkey}
        self.sourcing = dict(tmp.items() + kwargs.items())