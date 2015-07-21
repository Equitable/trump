from trump.orm import Symbol, SetupTrump, SymbolManager, ConversionManager, \
                  SymbolLogEvent

from trump.reporting.objects import TrumpReport

from trump.templating.templates import GoogleFinanceFT, YahooFinanceFT,\
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

#    def test_api_failure_causing_empty_feed(self):
#        """ This is an example of how to make a symbol that
#        is not allowed to be empty, but might be due to API problems,
#        and logs it when it happens"""
#        
#        sm = self.sm
#
#        sym = sm.create("orm_exc_test_symbol_a", overwrite=True)
#
#        testdata = os.path.join(curdir,'testdata','nonexistentdata.csv')
#
#        fdtemp = CSVFT(testdata, 'Amount', index_col=0)
#
#        sym.add_feed(fdtemp)
#  
#        sym.feeds[0].handle.api_failure['txtlog'] = True
#        sym.feeds[0].handle.api_failure['raise'] = False
#   
#        sym.feeds[0].handle.empty_feed['txtlog'] = True
#        sym.feeds[0].handle.empty_feed['raise'] = False
#        
#        sym.cache()

#    def test_actual_empty_feed(self):
#        """ This is an example of how to make a symbol that
#        is allowed to be empty, doesn't log or complain when it happens,
#        but will complain for other reasons (Eg. API Failure)"""
#
#        sm = self.sm
#
#        sym = sm.create("orm_exc_test_symbol_b", overwrite=True)
#
#        testdata = os.path.join(curdir,'testdata','emptydata.csv')
#
#        fdtemp = CSVFT(testdata, 'Amount', index_col=0)
#
#        sym.add_feed(fdtemp)
#   
#        sym.feeds[0].handle.empty_feed['raise'] = False
#        
#        sym.cache()
#  
#        assert sym.df.columns == pd.DataFrame(columns=[sym.name]).columns

#    def test_allowraise(self):
#        """ This is an example of how to setup problematic symbols,
#        and while caching a set of them, silencing the known problems
#        optionally."""
#
#        sm = self.sm
#
#        c1 = sm.create("orm_exc_test_symbol_c_good", overwrite=True)
#        c2 = sm.create("orm_exc_test_symbol_c_bad", overwrite=True)
#        c3 = sm.create("orm_exc_test_symbol_c_okay", overwrite=True)
#        
#        gooddata = os.path.join(curdir,'testdata','emptydata.csv')
#        fdtemp = CSVFT(gooddata, 'Amount', index_col=0)
#        c1.add_feed(fdtemp)
#        c1.feeds[0].handle.empty_feed['raise'] = False
#        c1.feeds[0].handle.empty_feed['report'] = True
#
#        baddata = os.path.join(curdir,'testdata','nonexistentdata.csv')
#        fdtemp = CSVFT(baddata, 'Amount', index_col=0)
#        c2.add_feed(fdtemp)
#        c2.feeds[0].handle.api_failure['report'] = True
#        
#        gooddata = os.path.join(curdir,'testdata','testdata.csv')
#        fdtemp = CSVFT(gooddata, 'Amount', index_col=0)
#        c3.add_feed(fdtemp)
#        
#        def trytocache(allowraise):
#            tr = TrumpReport("allowraisetestreport")
#            for sym in [c1, c2, c3]:
#                rep = sym.cache(allowraise=allowraise)
#                tr.add_symbolreport(rep)
#            return tr
#        
#        repf = trytocache(False)
#        sreports = repf.sreports
#        for i in range(len(sreports)):
#            sreport = sreports[i]
#            for j in range(len(sreport.freports)):
#                freport = sreport.freports[j]
#                for k in range(len(freport.handlepoints)):
#                    handlepoint = freport.handlepoints[j]
#                    if i == j == k == 0 :
#                        assert handlepoint.hpoint == 'empty_feed'
#                    if i == 1 and j == k == 0 :
#                        assert handlepoint.hpoint == 'api_failure'
#
#        with pytest.raises(IOError):
#            trytocache(True)

#    def test_multireportdf(self):
#        """ This is an example of how to setup problematic symbols,
#        and while caching a set of them, silencing the known problems
#        optionally."""
#
#        sm = self.sm
#
#        d1 = sm.create("orm_exc_test_symbol_d_good", overwrite=True)
#        d2 = sm.create("orm_exc_test_symbol_d_bad", overwrite=True)
#        d3 = sm.create("orm_exc_test_symbol_d_okay", overwrite=True)
#        
#        emptydata = os.path.join(curdir,'testdata','emptydata.csv')
#        baddata = os.path.join(curdir,'testdata','nonexistentdata.csv')
#        gooddata = os.path.join(curdir,'testdata','testdata.csv')
#        
#        d1.add_feed(CSVFT(emptydata, 'Amount', index_col=0))
#        d1.add_feed(CSVFT(baddata, 'Amount', index_col=0)) 
#        d1.add_feed(CSVFT(emptydata, 'Amount', index_col=0)) 
#        d1.add_feed(CSVFT(gooddata, 'Amount', index_col=0))
#        
#        for i in range(4):
#            d1.feeds[i].handle.empty_feed['report'] = True
#            d1.feeds[i].handle.api_failure['report'] = True
#
#        d2.add_feed(CSVFT(baddata, 'Amount', index_col=0))
#        d2.add_feed(CSVFT(gooddata, 'Amount', index_col=0))
#        
#        d2.feeds[0].handle.api_failure['report'] = True
#        d2.feeds[1].handle.api_failure['report'] = True
#        
#        d3.add_feed(CSVFT(gooddata, 'Amount', index_col=0))
#        
#        tr = TrumpReport("testreport")
#        for sym in [d1, d2, d3]:
#            rep = sym.cache(allowraise=False)
#            tr.add_symbolreport(rep)
#        
#        print tr.hpdf

        
        