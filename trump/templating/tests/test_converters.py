
from trump.templating.converters import _ListConverter

class TestConverters(object):

    def test_attribute_based_list_convertable(self):

        class ListConvertable(_ListConverter):
            def __init__(self):
                self.attr1 = True
                self.attr2 = True
                self.attr3 = False

        lc = ListConvertable()

        assert lc.as_list == ['attr1', 'attr2']

    def test_custom_based_list_convertable(self):

        class ListConvertable(_ListConverter):
            def __init__(self):
                self.attr1 = True
                self.attr2 = True
                self.attr3 = False
                self.cust_list = ['a','b','c']

        lc = ListConvertable()

        assert lc.as_list == ['a','b','c']