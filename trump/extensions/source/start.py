def Quandl():
	import Quandl as q
	data = q.get(**kwargs)
	try:
		fn = kwargs['fieldname']
	except KeyError:
		raise KeyError("fieldname wasn't specified in Quandl Feed")

	try:
		data = data[fn]
	except KeyError:
		kemsg = """{} was not found in list of Quandle headers:\n
				 {}""".format(fn, str(data.columns))
		raise KeyError(kemsg)

def psycopg2():
	dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
	import psycopg2 as db
	con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}
	con = db.connect(**con_kwargs)
	raise NotImplementedError("pyscopg2")
def DBAPI():
	dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
	db = __import__(self.ses.bind.driver)
	con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}

	con = db.connect(**con_kwargs)
	cur = con.cursor()
 
	if kwargs['dbinstype'] == 'COMMAND':
		qry = kwargs['command']
	elif kwargs['dbinstype'] == 'KEYCOL':
		reqd = ['indexcol', 'datacol', 'table', 'keycol', 'key']
		rel = (kwargs[c] for c in reqd)
		qry = "SELECT {0},{1} FROM {2} WHERE {3} = '{4}' ORDER BY {0};"
		qry = qry.format(*rel)
	elif kwargs['dbinstype'] == 'TWOKEYCOL':
		reqd = ['indexcol', 'datacol', 'table', 'keyacol', 'keya', 'keybcol', 'keyb']
		rel = (kwargs[c] for c in reqd)
		qry = "SELECT {0},{1} FROM {2} WHERE {3} = '{4}' AND {5} = '{6}' ORDER BY {0};"
		qry = qry.format(*rel)
	else:
		raise NotImplementedError("The database type {} has not been created.".format(kwargs['dbinstype']))
	   
	cur.execute(qry)
		
	results = [(row[0], row[1]) for row in cur.fetchall()]
	con.close()
	if len(results):
		ind, dat = zip(*results)
	else:
		ind, dat = [], []
	data = pd.Series(dat, ind)

	try:
		dosum = kwargs['duphandler'] == 'sum'
	except:
		dosum = False
	if dosum:
		data = data.groupby(data.index).sum()

def SQLAlchemy():
	NotImplementedError("SQLAlchemy")
def PyDataCSV():
	from pandas import read_csv

	col = kwargs['data_column']
	del kwargs['data_column']
	
	fpob = kwargs['filepath_or_buffer']
	del kwargs['filepath_or_buffer']
	
	df = read_csv(fpob, **kwargs)
	
	data = df[col]

def PyDataDataReaderST():
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

def WorldBankST():
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

def BBFetch():
	global bbapi_connected
	global bbapi
	
	if not bbapi_connected:
		bbapi = bf.Getter.BBapi(clean=False)
		bbapi_connected = True
	
	bbsec = bbapi.GetSecurity(kwargs['elid'])
	data = bbsec.GetDataMostRecentFetchDaily(kwargs['valuefieldname'],KeepTime=False,KeepTimeZone=False)              
	
	try:
		dosum = kwargs['duphandler'] == 'sum'
	except:
		dosum = False
	if dosum:
		 data = data.groupby(data.index).sum()

def BBFetchBulk():
	global bbapi_connected
	global bbapi
	
	if not bbapi_connected:
		bbapi = bf.Getter.BBapi(clean=False)
		bbapi_connected = True

	security = bbapi.GetSecurity(kwargs['elid'])
   
	indexfilter = None
	
	if 'keep_list' in kwargs:
		keep_list = kwargs['keep_list'].split(", ")
		indexfilter = {'dividend_type' : keep_list}
		
	data = security.GetDataMostRecentFetchBulk(kwargs['fieldname'],indexfilter=indexfilter,columntoindex=kwargs['datecol'],datacolumn=kwargs['datacol'])

	try:
		dosum = kwargs['duphandler'] == 'sum'
	except:
		dosum = False
	if dosum:
		data = data.groupby(data.index).sum()
	
	try:
		croptime = kwargs['croptime']
	except:
		croptime = False
	
	if croptime:
		data.index = [t.to_datetime().date() for t in data.index]

def f():
    pass

ex = """
stype = '{}'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
{}
    def getseries(self, ses, **kwargs):
{}
    return data
"""
