
    
stype = 'BBFetch'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        import equitable.bpsdl as bf   
        self.bbapi = bf.Getter.BBapi(clean=False)
    def getseries(self, ses, **kwargs):
		
        bbsec = self.bbapi.GetSecurity(kwargs['elid'])
        data = bbsec.GetDataMostRecentFetchDaily(kwargs['valuefieldname'],KeepTime=False,KeepTimeZone=False)              
		
        try:
            dosum = kwargs['duphandler'] == 'sum'
        except:
            dosum = False
        if dosum:
            data = data.groupby(data.index).sum()
        
        return data