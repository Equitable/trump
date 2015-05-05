import traceback as tb
import warnings as wn
import sys
from reporting.objects import HandlePointReport

def trumpwarn(message, category=UserWarning, filename='', lineno=-1):
    print ("TRUMP WARNING: " + str(message))

wn.showwarning = trumpwarn


class Handler(object):

    def __init__(self, logic, name="No Name", msg=None):
        self.name = name
        self.logic = logic
        self.msg = msg or "There was a problem"

    def process(self):
        typ, val, tback = sys.exc_info()
        tbextract = tb.extract_tb(tback)
        
        ret = None

        if self.logic['stdout']:
            print "\nTRUMP:\n{}\nThe following traceback was provided".format(self.msg)
            tb.print_exc()

        if self.logic['warn']:
            tbstr = "The following information was provided in the traceback:\n"
            for stacklvl in tbextract:
                tbstr += "   File '{}', line {}, in {}\n".format(*stacklvl)
            tbstr += "{} : {}".format(typ.__name__, val)
            wn.warn(self.msg + "\n" + tbstr)

        if self.logic['email']:
            raise NotImplementedError()

        if self.logic['dblog']:
            raise NotImplementedError()

        if self.logic['txtlog']:
            raise NotImplementedError()

        if self.logic['report']:
            ret = HandlePointReport(self.name, tbextract)

        if self.logic['raise']:
            raise
        
        if not (ret is None):
            return ret
