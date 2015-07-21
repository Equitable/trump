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
        import pandas as pd
        self.pd = pd
        import equitable.bpsdl as bf  
        from equitable.errors.existence import NoData
        self.NoData = NoData
        self.bbapi = bf.Getter.BBapi(clean=False)
    def getseries(self, ses, **kwargs):
		
        bbsec = self.bbapi.GetSecurity(kwargs['elid'])

        if kwargs['bbtype'] == 'COMMON':
            # Bloomberg raises an exception, when there is no data returned.
            # Trump, has validity functionality, that should be used to catch empty feeds that data should exist for.
            # So, just pass it on, and let it go get caught/logged/whatever, at the handle point...
            try:
                data = bbsec.GetDataMostRecentFetchDaily(kwargs['valuefieldname'],KeepTime=False,KeepTimeZone=False)
            except self.NoData:
                data = self.pd.Series()
        elif kwargs['bbtype'] == 'BULK':            
            indexfilter = None
            
            if 'keep_list' in kwargs:
                keep_list = kwargs['keep_list'].split(", ")
                indexfilter = {'dividend_type' : keep_list}

            try:                
                data = bbsec.GetDataMostRecentFetchBulk(kwargs['fieldname'],indexfilter=indexfilter,columntoindex=kwargs['datecol'],datacolumn=kwargs['datacol'])
            except self.NoData:
                data = self.pd.Series()
                
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