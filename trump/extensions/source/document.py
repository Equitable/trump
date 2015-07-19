from imp import find_module, load_module
import os

curdir = os.path.dirname(os.path.realpath(__file__))

extension_names = [n for n in os.listdir(curdir) if os.path.isdir(os.path.join(curdir, n)) ]

sources = {}
for name in extension_names:
    ext = find_module(name, [curdir])
    mod = load_module(name, *ext)
    sources[name] = mod
    

extension_names.sort()

with open('preinstalled.rst','w+') as f:
    
    f.write(""".. This page is auto generated via trump/extensions/document.py\n""" + \
            """.. Editing it, is silly, as it will be overwritten.  The docstring\n""" + \
            """.. of the modules should themselves be edited.\n\n""")
    f.write("Pre-Installed Source Extensions\n")
    f.write("-------------------------------\n\n")

    for name in extension_names:
        title = sources[name].stype
        extf = name.replace("tx-","") + "ext"
        
        def wl(s):
            f.write(s + "\n")
            
        wl(title)
        wl("^" * len(title))
        wl(".. code-block:: python")
        wl("")
        wl("   # the directory is %s" % name)
        wl("   stype = '%s'" % sources[name].stype)
        wl("   renew = %s" % sources[name].renew)
        
        doc = getattr(sources[name], extf)
        doc = getattr(doc, "__doc__")
        
        if doc:
            wl(doc)
        wl("")