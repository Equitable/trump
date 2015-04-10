
from ..templates import QuandlFT, QuandlSecureFT, GoogleFinanceFT

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
                                  'start': '2000-01-01,
                                  'end': 'now',
                                  'data_source' : 'google',
                                  'data_column' : 'Close'}
        assert ftemp.meta == {'stype' : 'PyDataDataReaderST'}
