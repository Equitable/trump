# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 21:06:12 2015

@author: Jeffrey
"""

pab = 'pandas_attribute_based'

class mixin_pab(object):
    def bld_abs(self):
        self.abs = {'mtype' : pab, 'kwargs' : {}}
    def bld_pct_change(self,**kwargs):
        self.pct_change = {'mtype' : pab, 'kwargs' : kwargs}
    def bld_add(self,**kwargs):
        self.add = {'mtype' : pab, 'kwargs' : kwargs}
    def _bld_pab_generic(self,funcname,**kwargs):
        margs = {'mtype' : pab, 'kwargs' : kwargs}
        self.__setattr__(funcname, margs)

pnab = 'pandas_nonattribute_based'

class mixin_pnab(object):
    def bld_rolling_mean(self,**kwargs):
        self.rolling_mean = {'mtype' : pnab, 'kwargs' : kwargs}
    def _bld_pnab_generic(self,funcname,**kwargs):
        margs = {'mtype' : pnab, 'kwargs' : kwargs}
        self.__setattr__(funcname, margs)