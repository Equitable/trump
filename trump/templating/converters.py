"""
Creates object converters, which take an object's attributes and build
other versions of them using common python objects.
"""
###############################################################################
#
# PyLint tests that will never be applied by Trump.
#
# instance of ... has no X member, ignored because we check for their existence
#                       prior to use.  They are an optional member.
# pylint: disable-msg=E1101
#
# Too many/few arguments, ignored, because this is part of the design.
#
# pylint: disable-msg=R0913
# pylint: disable-msg=R0903

from collections import OrderedDict as odict

class _ListConverter(object):
    """
    any custom object that implements attributes which only store boolean
    values, and therefore can be converted into a list by inspecting it's
    attributes and values.
    """
    @property
    def as_list(self):
        """
        returns a list version of the object, based on it's attributes
        """
        if hasattr(self, 'cust_list'):
            return self.cust_list
        if hasattr(self, 'attr_check'):
            self.attr_check()
        cls_bltns = set(dir(self.__class__))
        ret = [a for a in dir(self) if a not in cls_bltns and getattr(self, a)]
        return ret


class _DictConverter(object):
    """
    any custom object that can be converted into a dictionary by inspecting it's
    attributes and values.
    """
    @property
    def as_dict(self):
        """
        returns an dict version of the object, based on it's attributes
        """
        if hasattr(self, 'cust_dict'):
            return self.cust_dict
        if hasattr(self, 'attr_check'):
            self.attr_check()
        cls_bltns = set(dir(self.__class__))
        return {a: getattr(self, a) for a in dir(self) if a not in cls_bltns}


class _OrderedDictConverter(object):
    """
    any custom object that can be converted into an ordered dictionary
    by inspecting it's attributes and their values, plus the order they
    were added in.
    """
    def __init__(self):
        self.attrorder = []

    @property
    def as_odict(self):
        """
        returns an odict version of the object, based on it's attributes
        """
        if hasattr(self, 'cust_odict'):
            return self.cust_odict
        if hasattr(self, 'attr_check'):
            self.attr_check()
        odc = odict()
        for attr in self.attrorder:
            odc[attr] = getattr(self, attr)
        return odc

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name != 'attrorder':
            self.attrorder.append(name)
