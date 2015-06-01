import pandas as pd

class MetaMatrix(object):
    def __init__(self, symbols):
        rows = {}     
        self.symbols = symbols
        for sym in self.symbols:
            rows[sym.name] = {m.attr : m.value for m in sym.meta}
        self.result = pd.DataFrame.from_dict(rows, orient='index')
        self.result = self.result.sort()
        self.result.index.name = "trumpsym"
        self.attr = list(self.result.columns)
        
    def __call__(self, inc=None):
        if inc is None:
            inc = self.attr
        elif isinstance(inc, (str, unicode)):
            inc = [inc]
        else:
            assert isinstance(inc, list)
        return self.result[inc].sort(inc)