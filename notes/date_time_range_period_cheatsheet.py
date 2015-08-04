import pandas as pd
from datetime import datetime as dt
from datetime import date as d


a = [True, True, False, True, False]

for b in a:
    if b:
        continue
    print b
    
def explain(func):
    def afunc(*args, **kwargs):
        return func(*args, **kwargs)
    ind, df = afunc()
    print " " * 1 + "*" * 3 + " {} ".format(func.__name__.replace("_"," ").upper()) + "*" * 3
    print type(ind), ind[0]
    print "{} | {} | {} | {} ".format(df.index.__class__.__name__, df.index.dtype, df.index[0], repr(df.index[0]))
    return afunc

@explain    
def datetimes_a():
    datetimes = [dt(2015,1,i) for i in range(1,20)]
    datetimes_df = pd.DataFrame(index=datetimes, data=range(len(datetimes)))
    return datetimes, datetimes_df

@explain    
def datetimes_a_conv():
    datetimes = [dt(2015,1,i) for i in range(1,20)]
    datetimes_ind = pd.DatetimeIndex(datetimes)
    datetimes_df = pd.DataFrame(index=datetimes_ind, data=range(len(datetimes)))
    return datetimes_ind, datetimes_df

@explain    
def dates_a():
    dates = [d(2015,1,i) for i in range(1,20)]
    dates_df = pd.DataFrame(index=dates, data=range(len(dates)))
    return dates, dates_df

@explain    
def dates_conv_a():
    dates = [d(2015,1,i) for i in range(1,20)]
    dates_ind = pd.DatetimeIndex(dates)
    dates_df = pd.DataFrame(index=dates_ind, data=range(len(dates)))
    return dates_ind, dates_df

@explain    
def date_range_a():
    date_range_ind_D = pd.date_range('2015-01-01','2015-02-01',freq='D')
    date_range_ind_D_df = pd.DataFrame(index=date_range_ind_D, data=range(len(date_range_ind_D)))
    return date_range_ind_D, date_range_ind_D_df

@explain    
def period_range_a():
    period_range_ind_D = pd.period_range('2015-01-01','2015-02-01',freq='D')
    period_range_ind_D_df = pd.DataFrame(index=period_range_ind_D, data=range(len(period_range_ind_D)))
    return period_range_ind_D, period_range_ind_D_df

@explain    
def strings_a():
    str_ind = list('ABCDEF')
    str_df = pd.DataFrame(index=str_ind, data=range(len(str_ind)))
    return str_ind, str_df
    
##DatetimeIndex, np.dtype('<M8[ns]') ie. datetime64[ns]
#
#
##.index -> Index, np.dtype('O') ie. dtype='object'
##.index[0] -> datetime.date(2015, 1, 1)
#
#dates_df = pd.DataFrame(index=dates_ind, data=range(len(dates)))
##.index -> DatetimeIndex with dtype = datetime64[ns]
##.index[0] -> Timestamp('2015-01-01 00:00:00')
#
#date_range_ind_D = pd.date_range('2015-01-01','2015-02-01',freq='D')
#date_range_ind_B = pd.date_range('2015-01-01','2015-02-01',freq='B')
#date_range_ind_M = pd.date_range('2015-01-01','2015-12-01',freq='M')
#date_range_ind_Q = pd.date_range('2015-01-01','2015-12-01',freq='Q')
#date_range_ind_A = pd.date_range('2010-01-01','2015-12-01',freq='A')
#date_range_df = pd.DataFrame(data=range(len(date_range_ind_M)), index=date_range_ind_M)
#
#period_range_ind_D = pd.period_range('2015-01-01','2015-02-01',freq='D')
#period_range_ind_M = pd.period_range('2015-01-01','2015-12-01',freq='M')
#period_range_ind_Q = pd.period_range('2015-01-01','2015-12-01',freq='Q')
#period_range_ind_A = pd.period_range('2010-01-01','2015-12-01',freq='A')
#
#for d in dir(dates_df.index.__class__):
#    print dates_df.index.__class__.__name__
#    #ans = getattr(dates_df.index.__class__,d)
#    #anss = repr(ans)
#    #if "unbound" not in anss:
#    #    print d, "=", ans
#    