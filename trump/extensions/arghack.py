# -*- coding: utf-8 -*-
"""
Created on Sat Jan 24 21:33:09 2015

@author: Jeffrey
"""

def unpack(adict,argnames):
    if 'kwargs' in argnames:
        return adict
        
    offset = [int(x[3:]) for x in adict if x[:3] == 'arg']
    if len(offset) == 0:
        offset = 0
    else:
        offset = min(offset)
        
    #print "offset = {}".format(offset)
    ret = {}
    for i,arg in enumerate(argnames):
        #print i,arg
        if arg in adict:
            #print "arg in adict"
            k = arg
            ret[arg] = adict[k]            
        elif 'arg' + str(i+offset) in adict:
            #print "'arg' + str(i+offset) in adict"
            k = 'arg' + str(i+offset)
            ret[arg] = adict[k]
    return ret

def unpacker(f,ignore=None):
    if ignore == None:
        def wrapped_f(*args,**kwargs):
            allargs = {'arg' + str(i) : args[i] for i in range(len(args))} 
            allargs = dict(allargs.items() + kwargs.items())
            var_list = f.func_code.co_varnames
            goodkwargs = unpack(allargs,var_list)
            return f(**goodkwargs)
        return wrapped_f
    else:
        def wrapped_f(ig,*args,**kwargs):
            #print "ig = {}".format(ig)
            allargs = {'arg' + str(i+1) : args[i] for i in range(len(args))} 
            #print "allargs = {}".format(allargs)
            allargs = dict(allargs.items() + kwargs.items())
            #print "allargs = {}".format(allargs)
            var_list = [v for v in f.func_code.co_varnames if v != ignore]
            #print "var_list = {}".format(var_list)
            goodkwargs = unpack(allargs,var_list)
            #print "goodkwargs = {}".format(goodkwargs)
            return f(ig,**goodkwargs)
        return wrapped_f
    
if __name__ == '__main__':
    def myfunc(a,b,c):
        print a,b,c
        return 5
    
    print "myfunc " * 5
    
    myfunc = unpacker(myfunc)

    myfunc(1,2,3,4,5)
    myfunc(arg0=4,arg1=5,arg2=6)
    myfunc(a=7,b=8,c=9)
    myfunc(c=12,b=11,a=10)
      
    def myfunc2(a,b,c='C-DEFAULT'):
        print a,b,c
        return 5

    print "myfunc2 " * 5
    myfunc2 = unpacker(myfunc2,'a')
    

    myfunc2(0.1,0.2,0.3)
    bonus={'eight':8,'nine':9}
    myfunc2(1,(4,5),6,c=3,b=2,seven=7,**bonus) #too many args, doesn't error.
    myfunc2(4,arg1=5,arg2=6) #So long as 
    myfunc2(7,arg3=8,arg4=9)
    myfunc2(10,b=11) #partial kwargs
    myfunc2(12,b=13,c=14) #partial kwargs
    myfunc2(15,c=17,b=16) #switched order       