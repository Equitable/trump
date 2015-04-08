
from trump.templating.templates import QuandlFT

class TestTemplates(object):

    def test_quandl_ft(self):
        ftemp = QuandlFT("xxx", trim_start="yyyy-mm-dd", authtoken="yyy")
        assert ftemp.sourcing == {'authtoken': 'yyy',
                                  'trim_start': 'yyyy-mm-dd',
                                  'dataset': 'xxx'}
