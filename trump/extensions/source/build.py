from inspect import getmembers, isfunction, getsourcelines
import start
import os

funcs = [v for k,v in getmembers(start) if isfunction(v)]

for f in funcs:
    if f.func_name != 'BBFetch':
        mn = f.func_name
        mnl = f.func_name.lower()
        os.mkdir(mnl)
    
        init = file(os.path.join(mnl,'__init__.py'),'w+')
        init.write("from {}ext import *".format(mnl))
        init.close()
    
        ext = file(os.path.join(mnl,'{}ext.py'.format(mnl)),'w+')
        
        code = getsourcelines(f)[0][1:]
        code = ["\t" + l for l in code]
        code = [l.replace("\t"," " * 4) for l in code]
        ext.write(start.ex.format(mn, "".join(code), "".join(code)))
        
        ext.close()