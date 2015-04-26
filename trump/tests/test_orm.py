from ..orm import SymbolManager

from ..templating.templates import GoogleFinanceFT, YahooFinanceFT,\
    SimpleExampleMT, CSVFT

import pandas as pd

import pytest

import os

import datetime as dt

class TestORM(object):

    def test_symbol_creation(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fd = GoogleFinanceFT("TSLA", start='2015-04-01', end='2015-04-13')

        sym.add_feed(fd)

        sym.cache()

        assert sym.df.ix['2015-04-10'][0] == 210.90

    def test_symbol_munging_mod(self):

        sm = SymbolManager()

        sym = sm.create("TSLA", overwrite=True)

        fdtemp = GoogleFinanceFT("TSLA")

        mgtemp = SimpleExampleMT(5,5)

        sym.add_feed(fdtemp,munging=mgtemp)

        sym.cache()

        df = sym.df
        assert round(df.ix['2015-03-20'][0], 4) == round(0.031638, 4)

    def test_symbol_frequency_mod(self):

        sm = SymbolManager()

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

    def test_two_symbols(self):

        sm = SymbolManager()

        sym = sm.create("MSFT", overwrite=True)

        fdgoog = GoogleFinanceFT("MSFT", start='2015-03-01', end='2015-03-10')
        fdyhoo = YahooFinanceFT("MSFT", start='2015-03-01', end='2015-03-14')

        sym.add_feed(fdgoog)
        sym.add_feed(fdyhoo)

        sym.cache()

        ans = sym.alldata()

        # the 13th is the last row, and it should be blank because
        # we only fetched through the 10th.
        # As of now, the third column from the last, is the 'google' feed.
        assert ans[-1][-3] is None

        df = sym.df

        assert sym.n_feeds == 2
        assert round(df.ix['2015-03-13'][0], 2) == 41.38

    def test_tags_and_search(self):

        sm = SymbolManager()

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

    def test_existence_deletion(self):

        sm = SymbolManager()

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

        sm = SymbolManager()

        sym = sm.create("new", overwrite=True)
        
        curdir = os.path.dirname(os.path.realpath(__file__))
        testdata = os.path.join(curdir,'testdata','testdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)

        sym.cache()

        df = sym.df
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[2][0] == 3
    
    def test_datetime_float_override_failsafe(self):
        
        sm = SymbolManager()

        sym = sm.create("dtflor", overwrite=True)
        
        curdir = os.path.dirname(os.path.realpath(__file__))
        testdata = os.path.join(curdir,'testdata','testdata.csv')

        fdtemp = CSVFT(testdata, 'Amount', index_col=0)

        sym.add_feed(fdtemp)
        
        sym.add_override(dt.date(2012, 12, 31), 5, user='tester',
                         comment='testcomment')

        sym.cache()

        df = sym.df
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[2][0] == 5

        sym.add_fail_safe(dt.date(2011, 12, 31), -1, user='tester',
                        comment='testcomment2')

        sym.cache()

        df = sym.df
        assert df.iloc[1][0] == -1        
    def test_symbol_describe(self):
        
        sm = SymbolManager()
        
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
        
        