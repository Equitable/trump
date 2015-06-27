from ..orm import Symbol, SetupTrump, SymbolManager, ConversionManager, \
                  SymbolLogEvent

from ..templating.templates import GoogleFinanceFT, YahooFinanceFT,\
    SimpleExampleMT, CSVFT, FFillIT, FeedsMatchVT, DateExistsVT, PctChangeMT

import pandas as pd

import pytest

import os

import datetime as dt

import shutil as sh


curdir = os.path.dirname(os.path.realpath(__file__))
inspect_reports = False

class TestORM_Exceptions(object):
    
    def setup_method(self, test_method):
        self.eng = SetupTrump()
        self.sm = SymbolManager(self.eng)

    def test_api_failure_causing_empty_feed(self):
        """ This is an example of how to make a symbol that
        is not allowed to be empty, but might be due to API problems,
        and logs it when it happens"""
        
        sm = self.sm

        sym = sm.create("orm_exc_test_symbol_a", overwrite=True)

        testdata = os.path.join(curdir,'testdata','nonexistentdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
  
        sym.feeds[0].handle.api_failure['txtlog'] = True
        sym.feeds[0].handle.api_failure['raise'] = False
   
        sym.feeds[0].handle.empty_feed['txtlog'] = True
        sym.feeds[0].handle.empty_feed['raise'] = False
        
        sym.cache()

    def test_actual_empty_feed(self):
        """ This is an example of how to make a symbol that
        is allowed to be empty, doesn't log or complain when it happens,
        but will complain for other reasons (Eg. API Failure)"""

        sm = self.sm

        sym = sm.create("orm_exc_test_symbol_b", overwrite=True)

        testdata = os.path.join(curdir,'testdata','emptydata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
   
        sym.feeds[0].handle.empty_feed['raise'] = False
        
        sym.cache()
  
        assert sym.df.columns == pd.DataFrame(columns=[sym.name]).columns