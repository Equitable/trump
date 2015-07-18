"""
Required kwargs:

- 'elid' 
- 'bbtype' = ['COMMON', 'BULK'], then a few relevant kwargs depending on each.

Optional kwargs:

- 'duphandler' - 'sum'
- 'croptime' - boolean

"""
    
stype = 'BBFetch'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        import equitable.bpsdl as bf   
        self.bbapi = bf.Getter.BBapi(clean=False)
    def getseries(self, ses, **kwargs):
		
        bbsec = self.bbapi.GetSecurity(kwargs['elid'])

        if kwargs['bbtype'] == 'COMMON':
            data = bbsec.GetDataMostRecentFetchDaily(kwargs['valuefieldname'],KeepTime=False,KeepTimeZone=False)
        elif kwargs['bbtype'] == 'BULK':            
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

        return data