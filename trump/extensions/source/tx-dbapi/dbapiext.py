"""
The DBAPI driver, will use by default the same driver SQLAlchemy is using for trump. 
There is currently no way to change this default.  It's assumed that the driver
is DBAPI 2.0 compliant.

Required kwargs include:

- 'dbinsttype' which must be one of 'COMMAND', 'KEYCOL', 'TWOKEYCOL'
- 'dsn', 'user', 'password', 'host', 'database', 'port'

Optional kwargs include:

- duphandler ['sum'] which just groups duplicate index values together via the sum.

Additional kwargs:

Required based on 'dbinsttype' chosen:

'COMMAND' : 
- 'command' which is just a SQL string, where the first column becomes the index, and the second
column becomes the data.

'KEYCOL' :
- ['indexcol', 'datacol', 'table', 'keycol', 'key']

'TWOKEYCOL' :
- ['indexcol', 'datacol', 'table', 'keyacol', 'keya', 'keybcol', 'keyb']

"""
stype = 'DBAPI'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        db = __import__(ses.bind.driver)
        dbargs = ['dsn', 'user', 'password', 'host', 'database', 'port']
        con_kwargs = {k: v for k, v in kwargs.items() if k in dbargs}
    
        self.con = db.connect(**con_kwargs)
        import pandas as pd
        self.pd = pd
        
    def getseries(self, ses, **kwargs):
        cur = self.con.cursor()
     
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
        
        if len(results):
            ind, dat = zip(*results)
        else:
            ind, dat = [], []
        data = self.pd.Series(dat, ind)
    
        try:
            dosum = kwargs['duphandler'] == 'sum'
        except:
            dosum = False
        if dosum:
            data = data.groupby(data.index).sum()

        return data
