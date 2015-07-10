
from trump.tools.bitflags import BitFlag

class TestBitFlag(object):
    def test_instantiation(self):

        # From integer
        bf = BitFlag(0)
        assert bf.bin_str == '00000000'
        assert bf.val == 0

        # From dictionary
        bf = BitFlag({'raise' : True})
        assert bf.bin_str == '00000001'
        assert bf.val == 1

        # From list, with arbitrary flags set
        bf = BitFlag(['email','stdout'])
        assert repr(bf) == "BitFlag(36)"
        assert str(bf) == "raise warn EMAIL dblog txtlog STDOUT report"

    def test_mutability(self):

        bf = BitFlag(['email','stdout'])
        bf['email'] = False
        assert bf.email == False
        assert bf.val == 32

        bf['warn'] = True
        assert bf.warn == True
        assert bf.val == 34

    def test_asdict(self):

        expected = {'raise': False, 'stdout': True,
                    'txtlog': False, 'warn': False,
                    'dblog': False, 'report': False,
                    'email': True}

        bf = BitFlag(['email','stdout'])
        assert bf.asdict() == expected

        bf = BitFlag(expected)
        assert expected == bf.asdict()

    def test_logic(selfself):

        bf1 = BitFlag(['email','stdout'])
        bf2 = BitFlag(['warn','raise'])
        bf3 = bf1 & bf2
        assert bf3.val == 0
        bf4 = bf1 | bf2
        print bf4.val == 39

    def test_boollist(self):

        vals = [2 ** i for i in range(10)]
        vals = vals + [2 ** i + 1 for i in range(10)]
        vals = vals + [2 ** i - 1 for i in range(10)]
        vals = list(set(vals))
        vals.sort()

        for v in vals:
            bf = BitFlag(v)
            exp = "{0:08b}".format(v)[-8:]
            assert bf.bin_str == exp
            exp = [True if c == '1' else False for c in exp]
            msg = "{} != ".format(str(exp), str(bf.bools))
            assert exp[::-1] == bf.bools, msg


