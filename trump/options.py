# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 06:22:05 2015

@author: Jeffrey
"""

from ConfigParser import ConfigParser

cp = ConfigParser()

cp.read('private.cfg')

QuandlAPIkey = cp.get('Quandl','APIkey')