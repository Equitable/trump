import traceback as tb
import warnings as wn
import sys


def trumpwarn(message, category=UserWarning, filename = '', lineno = -1):
    print ("TRUMP WARNING: " + str(message))

wn.showwarning = trumpwarn

class Handler(object):
    def __init__(self, logic, msg=None):
        self.logic = logic
        self.msg = msg or "There was a problem"
    def process(self):
        print self.logic

        if self.logic['stdout']:
            print "\nTRUMP:\n{}\nThe following traceback was provided".format(self.msg)
            tb.print_exc()

        if self.logic['warn']:
            typ, val, tback = sys.exc_info()
            tbextract = tb.extract_tb(tback)
            tbstr = "The following information was provided in the traceback:\n"
            for stacklvl in tbextract:
                tbstr += "   File '{}', line {}, in {}\n".format(*stacklvl)
            tbstr += "{} : {}".format(typ.__name__, val)
            wn.warn(self.msg + "\n" + tbstr)

        if self.logic['email']: raise NotImplementedError()

        if self.logic['dblog']: raise NotImplementedError()

        if self.logic['txtlog']: raise NotImplementedError()

        if self.logic['report']: raise NotImplementedError()

        if self.logic['raise']:
            raise