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
extension_names = os.listdir('source')

for name in extension_names:
    ext = find_module(name, ['source'])
    mod = load_module(name, *ext)
    sources[mod.stype] = SourceExtension(mod)