"""
Creates the BitFlag and BitFlagType object,
which enables efficient storage of the boolean
array for each Handle catch points.
"""
from collections import OrderedDict as ODict
from sqlalchemy.types import TypeDecorator, Integer

from sqlalchemy.ext.mutable import Mutable


class BitFlag(Mutable, object):

    """
    An object used to encode and decode a boolean array
    as an an integer representing bitwise logic-flags.

    There are 7 hardcoded flags:

    - raise
    - warn
    - email
    - dblog
    - txtlog
    - stdout
    - report

    Each can be set to True or False, with convenience
    either at instantiation, or key-base set operations.

    Example of instatiation, setting the email and stdout
    flag to True::

        BitFlag(['email','stdout'])

    Example of instatiation, setting the email then,
    later setting stdout flag to True::

        bf = BitFlag(['email'])
        bf['stdout'] = True

    After either running either of these, the BitFlag
    will have a value of::

        >>> bf.val == 36
        True

        >>> print bf
        raise warn EMAIL dblog txtlog STDOUT report

        >>> print bf.bin_str
        00100100

        >>> print bf.email
        True

    ...because the 3rd and 6th bit are set.

    .. warning::

       Flag state can be read from the accessors named
       after the flags, however, they can't be written to.

    """
    flags = ['raise', 'warn', 'email', 'dblog',
             'txtlog', 'stdout', 'report']

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
        """

        # calculate an msb-like number, which is actually
        # the msb * 2 to get one more digit than
        # the number of flags

        self.msb = 2 ** (len(BitFlag.flags) + 1)

        # if an integer was passed...
        # convert it to a boolean array
        if isinstance(obj, int):
            self.val = obj % self.msb
            tmp = self.val + self.msb

            self.bools = []
            while tmp != 0:
                self.bools.append(tmp % 2 == 1)
                tmp >>= 1
            self.bools = self.bools[:-1]

            for i, key in enumerate(BitFlag.flags):
                setattr(self, key, self.bools[i])

        # a dict of the form {flags : bool, } was passed...
        # convert it to the boolean array just the same.
        elif isinstance(obj, (dict, list)):
            if isinstance(obj, list):
                obj = dict(zip(obj, [True] * len(obj)))
            # if there are defaultflags, use them, otherwise assume all flags
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

    # coerce is required to complete the SQLA mutability contract.
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, BitFlag):
            if isinstance(value, int):
                return BitFlag(value)
            return Mutable.coerce(key, value)
        else:
            return value

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
    
    def flagged(self):
        return [b.upper() if self[b] else b for b in BitFlag.flags]
    def __str__(self):
        tmp = self.flagged()
        return " ".join(tmp)

    def __repr__(self):
        return "BitFlag({})".format(self.val)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.bools[key]
        else:
            return self.__getattribute__(key)      
    def __setitem__(self, key, value):
        if isinstance(key, int):
            setattr(self, BitFlag.flags[key], value)
            self.bools[key] = value
        else:
            setattr(self, key, value)
            self.bools[BitFlag.flags.index(key)] = value            
        # recalculate the value from scratch...
        self.val = 0
        for i, val in enumerate(self.bools):
            if val:
                self.val += 2 ** i

        self.changed()

    def __call__(self):
        """
        Calling a BitFlag object returns it's integer value.

        :return: int
        """
        return self.val

    def __and__(self, other):
        """
        :param other: int, BitFlag

        BitFlag and integers work with the and
        operator using bitwise logic.

        :return: BitFlag
        """

        if isinstance(other, BitFlag):
            return BitFlag(other() & self())
        elif isinstance(other, int):
            return BitFlag(other & self())

    def __or__(self, other):
        """
        :param other: int, BitFlag

        BitFlag and integers work with the or
        operator using bitwise logic.

        :return: BitFlag
        """
        if isinstance(other, BitFlag):
            return BitFlag(other() | self())
        elif isinstance(other, int):
            return BitFlag(other | self())


class BitFlagType(TypeDecorator):

    """ 
    SQLAlchemy type definition for the BitFlag implementation.
    A BitFlag is a python object that wraps bitwise logic for hardcoded
    flags into a single integer value for quick database access and use."""

    impl = Integer
    
    def __init__(self, *args, **kwargs):
        super(BitFlagType, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """
        When SQLAlchemy binds a BitFlag, it converts it
        to an integer for storage in the database.
        """
        if value is not None:
            value = value.val
        return value

    def process_result_value(self, value, dialect):
        """
        When SQLAlchemy gets an integer from a BitFlagType
        column, it converts it to a BitFlag object.
        """
        if value is not None:
            value = BitFlag(value)
        return value

    def copy(self):
        return BitFlagType()

