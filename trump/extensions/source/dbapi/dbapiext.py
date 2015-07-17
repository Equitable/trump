
stype = DBAPI
renew = True

class Source(object):
    def __init__(ses, **kwargs):
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

    def getseries(ses, **kwargs):
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

