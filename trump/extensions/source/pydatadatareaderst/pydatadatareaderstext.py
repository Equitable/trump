
stype = PyDataDataReaderST
renew = True

class Source(object):
    def __init__(ses, **kwargs):
		import pandas.io.data as pydata
	
		fmt = "%Y-%m-%d"
		if 'start' in kwargs:
			kwargs['start'] = dt.datetime.strptime(kwargs['start'], fmt)
		if 'end' in kwargs:
			if kwargs['end'] == 'now':
				kwargs['end'] = dt.datetime.now()
			else:
				kwargs['end'] = dt.datetime.strptime(kwargs['end'], fmt)
	
		col = kwargs['data_column']
		del kwargs['data_column']
	
		adf = pydata.DataReader(**kwargs)
		data = adf[col]

    def getseries(ses, **kwargs):
		import pandas.io.data as pydata
	
		fmt = "%Y-%m-%d"
		if 'start' in kwargs:
			kwargs['start'] = dt.datetime.strptime(kwargs['start'], fmt)
		if 'end' in kwargs:
			if kwargs['end'] == 'now':
				kwargs['end'] = dt.datetime.now()
			else:
				kwargs['end'] = dt.datetime.strptime(kwargs['end'], fmt)
	
		col = kwargs['data_column']
		del kwargs['data_column']
	
		adf = pydata.DataReader(**kwargs)
		data = adf[col]

