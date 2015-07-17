
stype = 'PyDataCSV'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        from pandas import read_csv
    
        col = kwargs['data_column']
        del kwargs['data_column']
        
        fpob = kwargs['filepath_or_buffer']
        del kwargs['filepath_or_buffer']
        
        df = read_csv(fpob, **kwargs)
        
        data = df[col]

    def getseries(self, ses, **kwargs):
        from pandas import read_csv
    
        col = kwargs['data_column']
        del kwargs['data_column']
        
        fpob = kwargs['filepath_or_buffer']
        del kwargs['filepath_or_buffer']
        
        df = read_csv(fpob, **kwargs)
        
        data = df[col]

    return data
