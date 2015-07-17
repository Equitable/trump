
stype = Quandl
renew = True

class Source(object):
    def __init__(ses, **kwargs):
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

    def getseries(ses, **kwargs):
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

