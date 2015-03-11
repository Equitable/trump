class mixin_dbCon(object):
    def set_SoftCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):        
        """Derive the parameters right in the python file..."""
        self.dbcontype = "PARAM"
        self.dsn = '' #TODO Create for example purposes
        self.user = '' #TODO Create for example purposes
        self.password = '' #TODO Create for example purposes
        self.host = '' #TODO Create for example purposes
        self.database = '' #TODO Create for example purposes 
    def set_HardCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):
        """Store the parameters right in the python file..."""
        self.dbcontype = "PARAM"
        self.dsn = '' #TODO Create for example purposes
        self.user = '' #TODO Create for example purposes
        self.password = '' #TODO Create for example purposes
        self.host = '' #TODO Create for example purposes
        self.database = '' #TODO Create for example purposes 
    def set_LocalDB(self,dsn=None,user=None,password=None,host=None,database=None):           
        self.dbcontype = "PARAM"
        self.dsn = dsn or '' #TODO Read from config file
        self.user = user or '' #TODO Read from config file
        self.password = password or '' #TODO Read from config file
        self.host = host or '' #TODO Read from config file
        self.database = database or '' #TODO Read from config file
        
class mixin_dbIns(object):
    def set_keycol(self,table,keycol,key,datecol='date',valuecol='value'):
        self.dbinstype = "KEYCOL"
        self.table = table
        self.keycol = keycol
        self.key = key
        self.datecol = datecol
        self.valuecol = valuecol
        return self
    def set_basic(self,table=None,datecol='date',valuecol='value'):
        self.dbinstype = "BASIC"
        self.table = table or 'UNSPECIFIEDTABLE'
        self.datecol = datecol
        self.valuecol = valuecol
        return self
    def set_revbasic(self,table,revdatecol,datecol='date',valuecol='value'):
        self.dbinstype = "REVBASIC"
        self.table = table
        self.revdatecol = revdatecol
        self.datecol = datecol
        self.valuecol = valuecol
        return self

class mixin_attr_check(object):
    def attr_check(self):
        if hasattr(self,'table'):
            if self.table == 'UNSPECIFIEDTABLE':
                raise Exception("Unspecified table in tFeed-like object's sourcing argument.")