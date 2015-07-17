
stype = psycopg2
renew = True

class Source(object):
    def __init__(ses, **kwargs):
		dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
		import psycopg2 as db
		con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}
		con = db.connect(**con_kwargs)
		raise NotImplementedError("pyscopg2")

    def getseries(ses, **kwargs):
		dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
		import psycopg2 as db
		con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}
		con = db.connect(**con_kwargs)
		raise NotImplementedError("pyscopg2")

