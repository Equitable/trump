"""
All kwargs are passed to Quandl's API quandl.get()

An additional 'fieldname' is available to select a specific column if a specifc quandl DB,
doesn't support quandl's version of the same feature.

"""
stype = 'Quandl'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        import Quandl as q
        self.q = q

    def getseries(self, ses, **kwargs):
        data = self.q.get(**kwargs)
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

        return data
