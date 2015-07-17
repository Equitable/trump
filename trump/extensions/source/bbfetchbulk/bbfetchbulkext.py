
stype = BBFetchBulk
renew = True

class Source(object):
    def __init__(ses, **kwargs):
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

    def getseries(ses, **kwargs):
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

