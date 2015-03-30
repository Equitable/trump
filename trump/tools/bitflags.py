"""
Creates the BitFlag object, which enables efficient storage of the boolean
array for each Handle catch point.
"""
from collections import OrderedDict as ODict
import sqlalchemy.types as sqlatypes

class BitFlag(sqlatypes.TypeDecorator):
    """
    An object to semi-efficiently encode and decode a boolean array
    into and from an an integer representing bitwise logic based flags
    """
    flags = ['enabled', 'raise', 'warn', 'email',
             'dblog', 'txtlog', 'stdout', 'report']

    impl = sqlatypes.Integer

    def __init__(self, obj, defaultflags=None):
        """
        :param obj, (int, dict):
            either the decimal form of the bitwise array, or
            a dictionary (complete or otherwise) of the form
            {flag : bool, flag : bool, ...}
        :param defaultflags, dict:
            a dictionary representing the default for
            one or more flags.  Only applicable
            when a dictionary is passed to obj.  It's
            ignored when obj is an integer.
        :return:
            BitFlag
        """

        # calculate an msb-like number, which is actually
        # the msb * 2 to get one more digit than
        # the number of flags

        self.msb = 2 ** len(BitFlag.flags)

        # if an integer was passed...
        # convert it to a boolean array
        if isinstance(obj, int):
            self.val = obj % (self.msb >> 1)
            self.val += self.msb

            self.bools = []
            while self.val != 0:
                self.bools.append(self.val % 2 == 1)
                self.val >>= 1
            self.bools = self.bools[:-1]

            for i, key in enumerate(BitFlag.flags):
                setattr(self, key, self.bools[i])

        # a dict of the form {flags : bool, } was passed...
        # convert it to the boolean array just the same.
        elif isinstance(obj, dict):

            # if there are defaultflags, use them, otherwise assume all flages
            # are unset
            if defaultflags:
                defaults = defaultflags
            else:
                defaults = zip(BitFlag.flags, [False] * len(BitFlag.flags))
                defaults = ODict(defaults)

            self.bools = []
            self.val = 0
            for i, key in enumerate(BitFlag.flags):
                if key in obj:
                    val = obj[key]
                else:
                    val = defaults[key]
                setattr(self, key, val)
                self.bools.append(val)
                if val:
                    self.val += 2 ** i

    @property
    def bin(self):
        """ the binary equivalent """
        return bin(self.val)

    @property
    def bin_str(self):
        """ the binary equivalent, as a string """
        return str(bin(self.val + self.msb))[3:]

    def asdict(self):
        """ convert the flags to a dictionary, with keys as flags. """
        return {bit: self[bit] for bit in BitFlag.flags}

    def __str__(self):
        tmp = [b.upper() if self[b] else b for b in BitFlag.flags]
        return " ".join(tmp)

    def __repr__(self):
        return "BitFlag({})".format(self.val)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        self.bools[BitFlag.flags.index(key)] = value
        # recalculate the value from scratch...
        self.val = 0
        for i, val in enumerate(self.bools):
            if val:
                self.val += 2 ** i

    def __call__(self):
        return self.val

    def __and__(self, other):
        if isinstance(other, BitFlag):
            return BitFlag(other() & self())
        elif isinstance(other, int):
            return BitFlag(other & self())

    def __or__(self, other):
        if isinstance(other, BitFlag):
            return BitFlag(other() | self())
        elif isinstance(other, int):
            return BitFlag(other | self())

    def process_bind_param(self, value, dialect):
        return value.val # or should this be self.val?

    def process_result_value(self, value, dialect):
        return BitFlag(value)

    def copy(self):
        return BitFlag(self.val)