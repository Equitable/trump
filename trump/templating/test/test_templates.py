
from trump.templating.templates import QuandlFT, QuandlSecureFT, \
                        GoogleFinanceFT, YahooFinanceFT, StLouisFEDFT, \
                        EconFT, CSVFT

class TestTemplates(object):

    def test_quandl_ft(self):
        ftemp = QuandlFT("xxx", trim_start="yyyy-mm-dd", authtoken="yyy")
        assert ftemp.sourcing == {'authtoken': 'yyy',
                                  'trim_start': 'yyyy-mm-dd',
                                  'dataset': 'xxx'}

    def test_quandl_secure_ft(self):
        ftemp = QuandlSecureFT("xxx", trim_start="yyyy-mm-dd")
        assert ftemp.sourcing == {'trim_start': 'yyyy-mm-dd',
                                  'dataset': 'xxx'}
        assert ftemp.meta == {'sourcing_key' : 'userone',
                              'stype' : 'Quandl'}

    def test_google_finance_ft(self):
        ftemp = GoogleFinanceFT("xxx")
        assert ftemp.sourcing == {'name': 'xxx',
                                  'start': '1995-01-01',
                                  'end': 'now',
                                  'data_source' : 'google',
                                  'data_column' : 'Close'}
        assert ftemp.meta == {'stype' : 'PyDataDataReaderST'}

    def test_yahoo_finance_ft(self):
        ftemp = YahooFinanceFT("xxx")
        assert ftemp.sourcing == {'name': 'xxx',
                                  'start': '1995-01-01',
                                  'end': 'now',
                                  'data_source' : 'yahoo',
                                  'data_column' : 'Close'}
        assert ftemp.meta == {'stype' : 'PyDataDataReaderST'}

    def test_st_louis_fred_ft(self):
        ftemp = StLouisFEDFT("xxx")
        assert ftemp.sourcing == {'name': 'xxx',
                                  'start': '1995-01-01',
                                  'end': 'now',
                                  'data_source' : 'fred',
                                  'data_column' : 'xxx'}
        assert ftemp.meta == {'stype' : 'PyDataDataReaderST'}

    def test_econ_ft(self):
        ftemp = EconFT("xxx")
        assert ftemp.sourcing == {'datacol': 'value',
                                  'indexcol': 'date',
                                  'keycol': 'name',
                                  'user': 'username',
                                  'key': 'xxx',
                                  'table': 'econ',
                                  'database' : 'adatabase',
                                  'password': 'password123',
                                  'dbinstype': 'KEYCOL'}
        assert ftemp.meta == {'sourcing_key': 'explicit',
                              'stype': 'DBAPI'}
    
    def test_csv_ft(self):
        ftemp = CSVFT(r"C:\myfile.csv",'A',testarg='testval')
        assert ftemp.sourcing == {'filepath_or_buffer': r"C:\myfile.csv",
                                  'data_column': 'A',
                                  'testarg': 'testval'}

        assert ftemp.meta == {'stype': 'PyDataCSV'}
