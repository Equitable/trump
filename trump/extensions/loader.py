from imp import find_module, load_module
import os

class SourceExtension(object):
    def __init__(self, mod):
        self.initialized = False
        self.mod = mod
        self.renew = mod.renew
        self.Source = mod.Source
    def __call__(self, _ses, **kwargs):
        if not self.initialized or self.renew:
            self.fetcher = self.Source(_ses, **kwargs)
            self.initialized = True
        return self.fetcher.getseries(_ses, **kwargs)

sources = {}

curdir = os.path.dirname(os.path.realpath(__file__))
sourcedir = os.path.join(curdir,'source')

extension_names = [n for n in os.listdir(sourcedir) if os.path.isdir(os.path.join(sourcedir, n)) ]

for name in extension_names:
    ext = find_module(name, [sourcedir])
    mod = load_module(name, *ext)
    sources[mod.stype] = SourceExtension(mod)