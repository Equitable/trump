"""
All kwargs are passed to panda's read_csv function.

Additional required kwargs:

- 'filepath_or_buffer' - should be an absolute path.  Relative will only work, if caching is only
performed by a python script which can access the relative path.

- 'data_column' - the specific column required, so to turn the dataframe into a series.
"""
stype = 'PyDataCSV'
renew = False

class Source(object):
    def __init__(self, ses, **kwargs):
        from pandas import read_csv
        self.read_csv = read_csv

    def getseries(self, ses, **kwargs):
    
        col = kwargs['data_column']
        del kwargs['data_column']
        
        fpob = kwargs['filepath_or_buffer']
        del kwargs['filepath_or_buffer']
        
        df = self.read_csv(fpob, **kwargs)
        
        data = df[col]

        return data
