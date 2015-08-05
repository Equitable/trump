from trump.orm import Symbol, SetupTrump, SymbolManager, ConversionManager, \
                  SymbolLogEvent

from trump.templating.templates import GoogleFinanceFT, YahooFinanceFT,\
    SimpleExampleMT, CSVFT, FFillIT, FeedsMatchVT, DateExistsVT, PctChangeMT

import pandas as pd
import pytest
from pytest import mark
skipif = mark.skipif

   
import os
import datetime as dt
import shutil as sh

import urllib2

def internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False

net_on = internet_on()
def requires_net(func):
    return skipif(not net_on, reason="Requires Internet")(func)
    
def floats_equal(a,b,d=4):
    return round(a,d) == round(b,d)

curdir = os.path.dirname(os.path.realpath(__file__))
inspect_reports = False

class TestORM(object):
    @classmethod
    def setup_class(cls):
        cls.eng = SetupTrump()
    def setup_method(self, test_method):
        self.sm = SymbolManager(self.eng)
    def teardown_method(self, test_method):
        self.sm.complete()
    def test_setuptrump(self):
        SymbolManager("sqlite://")
        SymbolManager()
    @requires_net
    def test_symbol_creation(self):

        sm = self.sm

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA", start='2015-04-01', end='2015-04-13')

        sym.add_feed(fd)

        sym.cache()

        assert sym.df.ix['2015-04-10'][0] == 210.90

    @requires_net
    def test_symbol_munging_mod(self):

        sm = self.sm

        sym = sm.create("TSLA", overwrite=True)

        fdtemp = GoogleFinanceFT("TSLA")

        mgtemp = SimpleExampleMT(5,5)

        sym.add_feed(fdtemp,munging=mgtemp)
        
        sym.cache()

        df = sym.df
        assert round(df.ix['2015-03-20'][0], 4) == round(0.031638, 4)
        
    @requires_net
    def test_symbol_pct_change_munge(self):

        sm = self.sm

        sym = sm.create("GOOG", overwrite=True)

        fdtemp = GoogleFinanceFT("GOOG")

        mgtemp = PctChangeMT()

        sym.add_feed(fdtemp, munging=mgtemp)
        
        sym.cache()

        df = sym.df

        assert round(df.ix['2015-05-08'][0], 4) == round(0.014170, 4)
        
        print df.tail(5)

    @requires_net
    def test_symbol_frequency_mod(self):

        sm = self.sm

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA", start='2015-02-01', end='2015-04-05')

        sym.add_feed(fd)

        sym.index.case = "asfreq"
        sym.index.setkwargs(freq='M', method='ffill')
        sm.ses.commit()

        sym.cache()

        df = sym.df
        assert df.ix['2015-03-31'][0] == 188.77

        assert df.index.freq == 'M'

    @requires_net
    def test_two_feeds(self):

        sm = self.sm

        sym = sm.create("MSFT", overwrite=True)

        fdgoog = GoogleFinanceFT("MSFT", start='2015-03-01', end='2015-03-10')
        fdyhoo = YahooFinanceFT("MSFT", start='2015-03-01', end='2015-03-14')

        sym.add_feed(fdgoog)
        sym.add_feed(fdyhoo)

        sym.cache()

        ans = sym._all_datatable_data()

        # the 13th is the last row, and it should be blank because
        # we only fetched through the 10th.
        # As of now, the third column from the last, is the 'google' feed.
        assert (ans[-1][-3] is None) or pd.isnull(ans[-1][-3])

        df = sym.df

        assert sym.n_feeds == 2
        assert round(df.ix['2015-03-13'][0], 2) == 41.38

    @requires_net
    def test_tags_and_search(self):

        sm = self.sm

        sym = sm.create("MSFT", overwrite=True)

        fdmsft = YahooFinanceFT("MSFT")
        sym.add_feed(fdmsft)
        sym.add_tags(['tech','software'])
        results = sm.search_tag('tech')

        msft = results[0]
        results = sm.search_tag('soft%')
        msft2 = results[0]
        assert msft2 is msft
        
        msft.del_tags('tech')
        results = sm.search_tag('tech')
        assert len(results) == 0
        
    def test_tags_and_search_feeds(self):
        
        sm = self.sm
        
        for s in ['vaf', 'vbf', 'vcg']:
            sym = sm.create(s, overwrite=True)
            testdata = os.path.join(curdir,'testdata','testdailydata.csv')
            fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
            sym.add_feed(fdtemp)
            if s == 'vaf':
                sym.add_tags('vvvvv') #Should not be returned in search.
            sym.feeds[0].add_tags([x * 5 for x  in list(s)])

        syms = sm.search_tag('vvvvv', symbols=True, feeds=False)
        assert len(syms) == 1      
        assert syms[0].name == 'vaf'
        
        syms = sm.search_tag('vvvvv', symbols=False, feeds=True)
        assert len(syms) == 3
        syms = None
        
        syms = sm.search_tag('vvvvv', symbols=True, feeds=True)
        assert len(syms) == 3

    def test_symbol_event_log(self):
        
        sm = self.sm
        
        s = 'evlg'
        sym = sm.create(s, overwrite=True)
        
        origdata = os.path.join(curdir,'testdata','testdailydata.csv')
        tmpdata = os.path.join(curdir,'testdata','testdailydatatmp.csv')
        
        sh.copy2(origdata,tmpdata)
        
        fdtemp = CSVFT(tmpdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)
        
        sym.cache()
        sym.cache(staleonly=False)
        gc = sym.last_cache()
        
        os.remove(tmpdata)
        
        try:
            sym.cache(staleonly=False)
        except:
            print "Expected to fail..."
            
        assert sym.last_cache() == gc
        lasttry = sym.last_cache('START')
        assert lasttry > gc
        
    def test_general_search(self):
        
        sm = self.sm
        
        for s in ['gsvaf', 'gsvbf', 'gsvcg']:
            sym = sm.create(s, overwrite=True)
            testdata = os.path.join(curdir,'testdata','testdailydata.csv')
            fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
            sym.add_feed(fdtemp)
            if s in ('gsvaf', 'gsvcg'):
                sym.add_tags('gsvvv') #Should not be returned in search.
            sym.set_description('exampledesc' + s)
            sym.add_meta(keyattr=s[::-1])
        
        syms = sm.search("gsvaf", name=True)
        assert len(syms) == 1

        syms = sm.search("gsvvv", tags=True)
        assert len(syms) == 2

        syms = sm.search("exampledesc%", desc=True)
        assert len(syms) == 3

        syms = sm.search(s[::-1], meta=True)
        assert len(syms) == 1
        assert isinstance(syms[0], Symbol)

        syms = sm.search(s[::-1], meta=True, stronly=True)
        assert len(syms) == 1
        assert isinstance(syms[0], (str, unicode))
    
    @requires_net
    def test_existence_deletion(self):

        sm = self.sm

        sym = sm.create("new", overwrite=True)

        fdtemp = YahooFinanceFT("NEW")

        sym.add_feed(fdtemp)

        assert sm.exists("new")
        assert sm.exists(sym)

        sm.delete(sym)

        assert not sm.exists('new')

        with pytest.raises(Exception) as excinfo:
            sm.delete(0)
        assert 'Invalid symbol' in excinfo.value.message

        assert not sm.exists(sym)

    def test_pydata_csv(self):

        sm = self.sm

        sym = sm.create("new", overwrite=True)
        
        testdata = os.path.join(curdir,'testdata','testdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)

        sym.cache()

        df = sym.df
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[2][0] == 3
    
    def test_datetime_float_override_failsafe(self):
        
        sm = self.sm

        sym = sm.create("dtflor", overwrite=True)
        
        testdata = os.path.join(curdir,'testdata','testdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
        
        sm.add_override(sym, dt.date(2012, 12, 31), 5, user='tester',
                         comment='testcomment')
        sym.cache()
        df = sym.df
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[2][0] == 5

        sm.add_fail_safe(sym, dt.date(2011, 12, 31), -1, user='tester',
                        comment='testcomment2')
        sym.cache()
        df = sym.df
        assert df.iloc[1][0] == -1        

        sm.add_override(sym, dt.date(2012, 12, 31), 4, user='tester',
                         comment='testcomment3')
        sm.add_fail_safe(sym, dt.date(2011, 12, 31), -2, user='tester',
                        comment='testcomment4')
        sym.cache()
        df = sym.df
        assert df.iloc[2][0] == 4
        assert df.iloc[1][0] == -2    

    def test_int_index_string_data_override_failsafe(self):
        
        sm = self.sm

        sym = sm.create("intstrdtflor", overwrite=True)
        
        testdata = os.path.join(curdir,'testdata','teststrdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
                                
        sym.index.indimp = "IntIndexImp"
        sym.dtype.datadef = "StrDataDef"
        
        sm.complete()

        testdata = os.path.join(curdir,'testdata','teststrdata2.csv')
        fdtemp = CSVFT(testdata, 'Amount', index_col=0)
        sym.add_feed(fdtemp)

        sm.add_override(sym, 2015, 'z', user='tester',
                         comment='testcomment6')
 
        sym.cache()
        df = sym.df

        assert isinstance(df.index, pd.Int64Index)
        assert isinstance(df.intstrdtflor[2010], str)
        assert df.intstrdtflor[2014] == 'e'
        assert df.intstrdtflor[2015] == 'z'

    def test_add_feed_post_cache(self):
        
        sm = self.sm

        sym = sm.create("onetwo", overwrite=True)
        
        testdata = os.path.join(curdir,'testdata','teststrdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
                                
        sym.dtype.datadef = "StrDataDef"
        
        sm.complete()
        
        sym.cache()

        testdata = os.path.join(curdir,'testdata','teststrdata2.csv')
        fdtemp = CSVFT(testdata, 'Amount', index_col=0)
        sym.add_feed(fdtemp)

        sym.cache()
        df = sym.df
        assert df.onetwo['2015-12-31'] == 'f'
        
        onetwo = sm.get("onetwo")
        
        #Why is this needed in postgres, but not sqlite?
        sm.complete()
        sm.delete("onetwo")
        
        sym = sm.create("onetwo", overwrite=True)
        sm.delete("onetwo")
        
    def test_symbol_describe(self):
        
        sm = self.sm
        
        sym = sm.create("describer", overwrite=True)
        
        fdtemp = CSVFT("fakefile.csv", 'Amount', index_col=0)
        sym.add_feed(fdtemp)

        fdtemp = CSVFT("fakefile2.csv", 'Amount', index_col=0)
        sym.add_feed(fdtemp)
        
        sym.add_tags(['atag', 'btag', 'ctag'])
        
        result = sym.describe
        
        exp_result = """Symbol = describer
                          tagged = atag, btag, ctag
                          aliased = describer
                          feeds:
                            0. CSVFT
                            1. CSVFT"""
        
        def stripit(s):
            return s.replace(" ", "").replace("\n","")
        
        assert stripit(result) == stripit(exp_result)

    def test_update_handle(self):
        
        sm = self.sm
        
        sym = sm.create("uht", overwrite=True)

        testdata = os.path.join(curdir,'testdata','testdata.csv')
        fdtemp = CSVFT(testdata, 'Amount', index_col=0)
        sym.add_feed(fdtemp)
        
        assert not sym.handle.validity_check.warn
        
        assert not sym.feeds[0].handle.api_failure.warn
               
        sym.update_handle({'validity_check' : 2})

        sym.feeds[0].update_handle({'api_failure' : 2})
        
        sym.cache()
        
        assert sym.handle.validity_check.warn
        
        assert sym.feeds[0].handle.api_failure.warn

    def test_index_templating(self):
        
        sm = self.sm
        
        sym = sm.create("indt", overwrite=True)
        
        weekly = FFillIT('W')
        sym.set_indexing(weekly)

        testdata = os.path.join(curdir,'testdata','testdailydata.csv')
        fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)
        
        sym.cache()
        
        assert sym.df.index.freq == 'W' 

    def test_validity_feed_match(self):
        
        sm = self.sm
        
        sym = sm.create("fmvttf", overwrite=True)
        
        fm = FeedsMatchVT(1,2)
        sym.add_validator(fm)

        testdata = os.path.join(curdir,'testdata','testdailydata.csv')
        fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)
        fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)
        
        sym.cache()

    def test_validity_date_exists(self):
        
        sm = self.sm
        
        sym = sm.create("devt", overwrite=True)
        
        fm = DateExistsVT(dt.date(2010,02,15))
        sym.add_validator(fm)

        testdata = os.path.join(curdir,'testdata','testdailydata.csv')
        fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)
        
        sym.cache()
    def test_index_kwargs(self):
        
        sm = self.sm
        
        sym = sm.create("tinkw", overwrite=True)

        testdata = os.path.join(curdir,'testdata','testdailydata.csv')
        fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
        sym.add_feed(fdtemp)

        tkwargs = {'A' : None, 'B' : 10, 'C' : 10.0, 'D' : 'test',
                   'E' : False, 'F' : dt.datetime(2010,10,10)}
        sym.index.setkwargs(**tkwargs)
        
        sm.complete()
        
        symn = sm.get('tinkw')
        
        actkwargs = symn.index.getkwargs()
        
        assert tkwargs == actkwargs

    def test_view_creation(self):
        
        sm = self.sm
        
        for s in ['va', 'vb', 'vc']:
            sym = sm.create(s, overwrite=True)
            sym.add_tags('testtagz')
            testdata = os.path.join(curdir,'testdata','testdailydata.csv')
            fdtemp = CSVFT(testdata, 'Amount', parse_dates=0, index_col=0)
            sym.add_feed(fdtemp)
            sm.complete()
            sym.cache()

        sm.build_view_from_tag('testtagz')
    def test_fx_converting(self):

        sm = self.sm

        fxdata = os.path.join(curdir,'testdata','fxdata3.csv')
        for pair in ['EURUSD', 'GBPUSD', 'CADUSD', 'AUDEUR', 'USDJPY']:
            print pair
            sym = sm.create(pair, overwrite=True)
            fdtemp = CSVFT(fxdata, pair, index_col=0)
            sym.add_feed(fdtemp)
            business_day = FFillIT('B')
            sym.set_indexing(business_day)
            #USDCAD -> "CAD/USD"
            sym.set_units("{}/{}".format(pair[3:], pair[:3]))
            sym.add_tags('forex')
            sym.cache()
        
        cm = ConversionManager(self.eng, 'FX', 'forex')
        
        #Should be the same as GBP...
        df = cm.get_converted('GBPUSD', 'USD')
        assert floats_equal(df.ix['2015-05-15'][0], 1.57370)

        #Should be ~1.88
        df = cm.get_converted('GBPUSD', 'CAD')
        assert floats_equal(df.ix['2015-05-15'][0], 1.88357)
               
        #Should be 1.0000
        df = cm.get_converted('GBPUSD', 'GBP')
        assert floats_equal(df.ix['2015-05-15'][0], 1.0)

        #Should be ~0.97
        df = cm.get_converted('AUDEUR', 'CAD')
        assert floats_equal(df.ix['2015-05-15'][0], 0.96678)

        #Should be ~187
        df = cm.get_converted('GBPUSD', 'JPY')
        assert floats_equal(df.ix['2015-05-15'][0], 187.7817525)

        #Should error...since CHF wasn't added.
        try:
            df = cm.get_converted('GBPUSD', 'CHF')
            assert False
        except Exception, exp:
            assert exp.message == "Converter has insufficient data to process USD to CHF"

    def test_real_trumpreport(self):

        sm = self.sm

        fxdata = os.path.join(curdir,'testdata','fxdata.csv')
        for pair in ['EURUSD', 'GBPUSD', 'USDCAD']:
            sym = sm.create(pair, overwrite=True)
            fdtemp = CSVFT(fxdata, pair, index_col=0)
            sym.add_feed(fdtemp)
            business_day = FFillIT('B')
            sym.set_indexing(business_day)
            sym.add_tags('forex_report')
        
        report = sm.bulk_cache_of_tag('forex_report')
        print report.html
        
        if inspect_reports:
            fout = file(os.path.join(curdir,'test_forex.html'),'w+')
            fout.write(report.html)
            fout.close()

    def test_search_meta(self):

        sm = self.sm

        for tikr in ['aaa', 'bbb', 'ccc']:
            sym = sm.create(tikr, overwrite=True)
            sym.add_meta(first = tikr[0].upper(), 
                         second = tikr[1:],
                         third = 'three')
        
        syms = sm.search_meta_specific(third='three')
        assert len(syms) == 3
        