# -*- coding: utf-8 -*-
"""
Trump's templating system consists of pure-python objects, which can
be converted into either lists, dictionaries, or ordered dictionaries,
which can then be used in the generalized constructors of Trump's SQLAlchemy 
based ORM system.
"""

from collections import OrderedDict as odict

from converters import  _ListConverter, _DictConverter, _OrderedDictConverter

class bTags(_ListConverter):
    """
    Tag Templates are any object which implements a property called 
    as_list, which returns a list of strings
    
    The Base Template for Tag Templates inherits from _listConverter, which
    implements as_list().  as_list() looks at the attributes defined and 
    set to True, in order to include the list of tags.
    """
    def __init__(self):
        pass
        #self.aTag = True
    def add_tag(self,tag):
        self.__setattr__(tag,True)

class bMunging(_OrderedDictConverter):
    """
    Munging Templates are any object which implements a property called 
    as_odict, which returns an odict where each key is a function in 
    munging_methods, and it's value is an object which represents the parameters
    to use on that object.  This should be sufficient to pass to a 
    a Feed constructor's munging parameter, which then becomes FeedMungingArgs objects
    making up a FeedMunge object, of which will be the instructions associated
    with a specific Feed object.
    """

    def __init__(self):
        super(bMunging,self).__init__()
        #self.key_one = 'value'
        #self.key_two = 'value' # This object tracks which order the attributes
                                # are created.

class bSource(_DictConverter):
    """
    Source Templates are any object which implements a property called
    as_dict.  The keywords and values of which are sufficient to pass to a 
    a Feed constructor's source parameter, which then become FeedSource objects
    making up a source.
    """
    def __init__(self):
        pass
        #self.key = 'value'
                             
class bFeed(object):
    """
    Feed objects need an tags, sourcing, munging and validity attribute
    defined.  They must be a list, dict, odict, and dict, respectively.
    """
    def __init__(self):
        self.ftype = self.__class__.__name__
        self.tags = []
        self.sourcing = {}
        self.munging = odict()
        self.validity = {}
        self.meta = {}
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

