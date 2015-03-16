from trump.options import read_settings

class mixin_dbCon(object):
#    def set_SoftCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):        
#        """Derive the parameters right in the python file..."""
#        #TODO
#        self.dsn = ''
#        self.user = ''
#        self.password = ''
#        self.host = ''
#        self.database = ''
#    def set_HardCodedDB(self,dsn=None,user=None,password=None,host=None,database=None):
#        """Store the parameters right in the python file..."""
#        self.dsn = dsn or ''
#        self.user = user or ''
#        self.password = password or ''
#        self.host = host or ''
#        self.database = database or ''
    def set_con_params(self,dsn=None,user=None,password=None,host=None,database=None,sourcing_key=None):
        if sourcing_key:
            settings = read_settings()['DBAPI'][sourcing_key]
            if 'dsn' in settings:
                self.dsn = dsn or settings['dsn']
            if 'user' in settings:
                self.user = user or settings['user']
            if 'password' in settings:
                self.password = password or settings['password']
            if 'host' in settings:
                self.host = host or settings['host']
            if 'database' in settings:
                self.database = database or settings['database']
        else:
            self.dsn = dsn or ''
            self.user = user or ''
            self.password = password or ''
            self.host = host or ''
            self.database = database or ''
    def set_con_params_secure(self,sourcing_key,dsn=None,user=None,password=None,host=None,database=None):
        self.sourcing_key = sourcing_key
        self.dsn = dsn or ''
        self.user = user or ''
        self.password = password or ''
        self.host = host or ''
        self.database = database or ''
            
class mixin_dbIns(object):
    def set_keycol(self,table,keycol,key,indexcol='date',datacol='value'):
        self.dbinstype = "KEYCOL"
        self.table = table
        self.keycol = keycol
        self.key = key
        self.indexcol = indexcol
        self.datacol = datacol
        return self
    def set_basic(self,table,indexcol='date',datacol='value'):
        self.dbinstype = "BASIC"
        self.table = table
        self.indexcol = indexcol
        self.datacol = datacol
        return self
    def set_revbasic(self,table,revdatecol,indexcol='date',datacol='value'):
        self.dbinstype = "REVBASIC"
        self.table = table
        self.revdatecol = revdatecol
        self.indexcol = indexcol
        self.datacol = datacol
        return self
    def set_command(self,command):
        self.dbinstype = "COMMAND"
        self.command = command
        return self

class mixin_attr_check(object):
    def attr_check(self):
        if hasattr(self,'table'):
            if self.table == 'UNSPECIFIEDTABLE':
                raise Exception("Unspecified table in tFeed-like object's sourcing argument.")