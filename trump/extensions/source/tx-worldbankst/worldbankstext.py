"""
Uses pandas.io.wb.download to query indicators, for a specific country.

country, must be a world bank country code.

Some assumptions as implied about the indicator and the first level of the index.  This 
may not work for all worldbank indicators.

"""
stype = 'WorldBankST'
renew = False

class Source(object):
    def __init__(self, ses, **kwargs):
        from pandas.io import wb
        self.wb = wb
    def getseries(self, ses, **kwargs):
        ind = str(kwargs['indicator'])
        cc = str(kwargs['country'])
        
        del kwargs['indicator']
        del kwargs['country']
        
        df = self.wb.download(indicator=ind, country=cc, errors='raise', **kwargs)
        firstlevel = df.index.levels[0][0]
        data = df.ix[firstlevel][ind]
    
        data = data.sort_index()
        data.index = data.index.astype(int)

        return data
