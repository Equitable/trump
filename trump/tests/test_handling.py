from trump.handling import Handler


from trump.tools.bitflags import BitFlag

import pytest

class TestHandling(object):

    def test_stdout(self):

        bf = BitFlag(['stdout'])
        try:
            raise Exception("Uh Oh")
        except:
            Handler(bf).process()

    def test_warn(self, recwarn):

        bf = BitFlag(['warn'])
        try:
            raise Exception("Uh Oh")
        except:
            Handler(bf).process()
            w = recwarn.pop()
            assert "Uh Oh" in str(w.message)


    def test_raise(self):

        bf = BitFlag(['raise'])
        try:
            raise Exception("Uh Oh")
        except:
            with pytest.raises(Exception) as excinfo:
                Handler(bf).process()
            assert 'Uh Oh' in excinfo.value

