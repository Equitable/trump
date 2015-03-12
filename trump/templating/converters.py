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
        if hasattr(self,'attr_check'):
            self.attr_check()
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
        if hasattr(self,'attr_check'):
            self.attr_check()
        class_builtins = set(dir(self.__class__))
        return {a : getattr(self,a) for a in dir(self) if a not in class_builtins}
        
class _OrderedDictConverter(object):
    def __init__(self):
        self.attrorder = []
    @property
    def as_odict(self):
        if hasattr(self,'cust_odict'):
            return self.cust_odict
        if hasattr(self,'attr_check'):
            self.attr_check()
        od = odict()
        for attr in self.attrorder:
            od[attr] = getattr(self,attr)
        return od
    def __setattr__(self, name, value):
        self.__dict__[name] = value 
        if name != 'attrorder':
            self.attrorder.append(name)