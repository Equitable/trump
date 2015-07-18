"""
This uses pandas.io.data.DataReader, all kwargs get passed to that.

start and end are optional, but must be of the form 'YYYY-MM-DD'.

Will default to since the beginning of available data, and run through "today".

data_column is required to be specified as well.

"""
stype = 'PyDataDataReaderST'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        import pandas.io.data as pydata
        import datetime as dt
        self.pydata = pydata
        self.dt = dt
    def getseries(self, ses, **kwargs):
        fmt = "%Y-%m-%d"
        if 'start' in kwargs:
            kwargs['start'] = self.dt.datetime.strptime(kwargs['start'], fmt)
        if 'end' in kwargs:
            if kwargs['end'] == 'now':
                kwargs['end'] = self.dt.datetime.now()
            else:
                kwargs['end'] = self.dt.datetime.strptime(kwargs['end'], fmt)
    
        col = kwargs['data_column']
        del kwargs['data_column']
    
        adf = self.pydata.DataReader(**kwargs)
        data = adf[col]

        return data
