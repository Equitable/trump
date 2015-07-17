
stype = WorldBankST
renew = True

class Source(object):
    def __init__(ses, **kwargs):
		from pandas.io import wb
	
		ind = str(kwargs['indicator'])
		cc = str(kwargs['country'])
		
		del kwargs['indicator']
		del kwargs['country']
		
		df = wb.download(indicator=ind, country=cc, errors='raise', **kwargs)
		firstlevel = df.index.levels[0][0]
		data = df.ix[firstlevel][ind]
	
		data = data.sort_index()
		data.index = data.index.astype(int)

    def getseries(ses, **kwargs):
		from pandas.io import wb
	
		ind = str(kwargs['indicator'])
		cc = str(kwargs['country'])
		
		del kwargs['indicator']
		del kwargs['country']
		
		df = wb.download(indicator=ind, country=cc, errors='raise', **kwargs)
		firstlevel = df.index.levels[0][0]
		data = df.ix[firstlevel][ind]
	
		data = data.sort_index()
		data.index = data.index.astype(int)

