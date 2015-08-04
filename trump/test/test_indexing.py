from trump.indexing import DatetimeIndexImp

from pandas.util.testing import assert_series_equal, assert_frame_equal

import pandas as pd
import datetime as dt

class TestDateTimeIndexImp(object):
    def test_iiasfreq(self):
        tst_ind = [dt.date(2015, 1, i) for i in range(1, 20)]
        tst_ind.append(dt.date(2015, 2, 5))
        
        tst_dat = [1.0] * len(tst_ind)
        
        tst_s = pd.Series(tst_dat, tst_ind)
        tst_df = pd.DataFrame(tst_dat, tst_ind)
        
        dii = DatetimeIndexImp('asfreq', freq='B')
        
        
        exp_ind = pd.date_range(start='20150101', end='20150205', freq='B')
        exp_dat = [1.0] * 13 + [pd.np.nan] * 12 + [1.0]
        exp_s = pd.Series(exp_dat, exp_ind)
        exp_df = exp_s.to_frame()
        
        assert_series_equal(dii.process_post_feed_cache(tst_s), exp_s, check_dtype=True,
                            check_index_type=True,
                            check_series_type=True)
                            
        assert_frame_equal(dii.process_post_orfs(tst_df), exp_df,
                           check_index_type=True)

    def test_iiasis(self):
        
        ind = [dt.date(2015,1,i) for i in range(1,30)]
        S1 = pd.Series(index=ind, data=range(len(ind)))
    
        ind = [dt.datetime(2015,1,i,0,0,0) for i in range(1,30)]
        S2 = pd.Series(index=ind, data=range(len(ind)))
        
        dtii = DatetimeIndexImp('asis')
        
        S1 = dtii.process_post_feed_cache(S1)
        S2 = dtii.process_post_feed_cache(S2)
        
        assert len(pd.concat([S1,S2],axis=1)) == 29

    def test_iiasis_with_time(self):
        
        ind = [dt.date(2015,1,i) for i in range(1,30)]
        S1 = pd.Series(index=ind, data=range(len(ind)))
    
        ind = [dt.datetime(2015,1,i,0,0,1) for i in range(1,30)]
        S2 = pd.Series(index=ind, data=range(len(ind)))
        
        dtii = DatetimeIndexImp('asis')
        
        S1 = dtii.process_post_feed_cache(S1)
        S2 = dtii.process_post_feed_cache(S2)
        
        assert len(pd.concat([S1,S2],axis=1)) == 29 * 2
        
    def test_guess(self):
        pass
    def test_guess_post(self):
        pass

# Not sure if something like this will be used...
# depends on if we can make some smarter setup and teardowns...
# is there a way to do this, with "nested" setup and teardowns?
        
class TestIndexImplementers(object):


    def test_integer_index_imp(self):
        pass
        #iii = IntIndexImp(...)

    def test_string_index_imp(self):
        pass
        #sii = StringIndexImp(...)

    def test_period_index_imp(self):
        pass
        #pii = PeriodIndexImp(...)