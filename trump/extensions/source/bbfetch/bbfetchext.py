
stype = BBFetch
renew = True

class Source(object):
    def __init__(ses, **kwargs):
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

    def getseries(ses, **kwargs):
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

