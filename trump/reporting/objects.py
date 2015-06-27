# -*- coding: utf-8 -*-
"""
Created on Mon May 04 06:49:37 2015

Creator: JMcLarty
"""
from __future__ import division
import sys
import traceback as trcbm
import pandas as pd

import datetime as dt

from collections import OrderedDict as odict

class HandlePointReport(object):
    def __init__(self, handlepoint, trace):
        self.hpoint = handlepoint
        self.trace = trace
    @property
    def df(self):
        return pd.DataFrame({'handlepoint' : self.hpoint, 
                            'tracelineno' : i, 
                            'file' : tr[0], 
                            'traceline' : tr[1], 
                            'tracefunc' : tr[2], 
                            'tracecode' : tr[3]} 
                            for i, tr in enumerate(self.trace))
    @property
    def html(self):
        return "{}\n{}".format(self.hpoint, self.trace[-3:])
        
class ReportPoint(object):
    def __init__(self, reportpoint, attribute, value, extended=None):
        self.rpoint = reportpoint
        self.attribute = attribute
        self.value = value
        self.extended = extended
    @property
    def df(self):
        return pd.DataFrame({'reportpoint' : self.rpoint, 'attribute' : self.attribute, 'value' : self.value, 'extended' : self.extended})
    @property
    def html(self):
        return "{} {} {}\n{}".format(self.rpoint, self.attribute, self.value,
                                    self.extended)

class FeedReport(object):
    def __init__(self, num):
        self.num = num
        self.tstamp = dt.datetime.now() 
        self.handlepoints = []
        self.reportpoints = []
    @property
    def hpdf(self):
        dfs = [hp.df for hp in self.handlepoints]
        if len(dfs):
            df = pd.concat(dfs, axis=0)
            df['tstamp'] = [self.tstamp] * len(df)
            df['feednum'] = [self.num] * len(df)
            return df
        else:
            return pd.DataFrame()
    def add_handlepoint(self, hpreport):
        self.handlepoints.append(hpreport)
    def add_reportpoint(self, rpoint):
        self.reportpoints.append(rpoint)
    def asodict(self, handlepoints=True, reportpoints=True):
        out = odict()
        if handlepoints:
            for hp in self.handlepoints:
                out[hp.hpoint] = hp.trace
        if reportpoints:
            for rp in self.reportpoints:
                if not (rp.rpoint in out):
                    out[rp.rpoint] = odict()
                out[rp.rpoint][self.attribute] = {'value' : rp.value, 'extended': rp.extended}
        return out
    @property
    def html(self):
        
        thtml = []
        
        thtml.append("<h3>{}</h3>".format(self.num))
        thtml.append("<h5>{}</h5>".format(self.tstamp))
        
        for hp in self.handlepoints:
            thtml.append(hp.html)
            thtml.append("<br>")
            
        for rp in self.reportpoints:
            thtml.append(rp.html)
            thtml.append("<br>")
            
        return "".join(thtml)
        
class SymbolReport(object):
    def __init__(self, name):
        self.name = name
        self.freports = []
        self.handlepoints = []
        self.reportpoints = []
    @property
    def hpdf(self):

        fddfs = [fd.hpdf for fd in self.freports]
            
        dfs = [hp.df for hp in self.handlepoints]
        if len(dfs):
            df = pd.concat(dfs, axis=0)
            df['tstamp'] = [0] * len(dfs)
            df['feednum'] = [-1] * len(dfs)
            fddfs.append(df)
        
        df = pd.concat(fddfs, axis=0)
        
        df['symbol'] = [self.name] * len(df)
    
        return df
    def add_feedreport(self, freport):
        self.freports.append(freport)
    def add_handlepoint(self, hpreport):
        self.handlepoints.append(hpreport)
    def add_reportpoint(self, rpoint):
        self.reportpoints.append(rpoint)
    def asodict(self, freports=True, handlepoints=True, reportpoints=True):
        out = odict()
        if freports:
            for fr in self.freports:
                out[fr.num] = {'tstamp' : fr.tstamp, 
                               'report' : fr.asodict(handlepoints, reportpoints)}           
        if handlepoints:
            for hp in self.handlepoints:
                out[hp.hpoint] = hp.trace
        if reportpoints:
            for rp in self.reportpoints:
                if not (rp.rpoint in out):
                    out[rp.rpoint] = odict()
                out[rp.rpoint][self.attribute] = {'value' : rp.value, 'extended': rp.extended}
        return out
    def all_handlepoints(self):
        out = odict()
        for fr in self.freports:
            for hp in fr.handlepoints:
                if not (hp.hpoint in out):
                    out[hp.hpoint] = []
                out[hp.hpoint].append((self.name, fr.num, hp.trace))
        for hp in self.handlepoints:
            if not (hp.hpoint in out):
                out[hp.hpoint] = []
            out[hp.hpoint].append((self.name, None, hp.trace))
        return out
    @property
    def html(self):
        
        thtml = []
        
        thtml.append("<h2>{}</h2>".format(self.name))
        
        for fr in self.freports:
            thtml.append(fr.html)
            thtml.append("<br>")
            
        for hp in self.handlepoints:
            thtml.append(hp.html)
            thtml.append("<br>")
            
        for rp in self.reportpoints:
            thtml.append(rp.html)
            thtml.append("<br>")            
        return "".join(thtml)
        

class TrumpReport(object):
    def __init__(self, name):
        self.name = name
        self.sreports = []
    def add_symbolreport(self, sreport):
        self.sreports.append(sreport)
    @property
    def hpdf(self):

        dfs = [sr.hpdf for sr in self.sreports]
            
        if len(dfs):
            dfs = pd.concat(dfs, axis=0)
            return dfs.reset_index(drop=True)
        else:
            return pd.DataFrame()
            
    @property
    def html(self):
        
        thtml = []
        
        thtml.append("<h1>{}</h1>".format(self.name))
        
        for sr in self.sreports:
            thtml.append(sr.html)
            thtml.append("<br>")
            
        return "".join(thtml)
    def all_handlepoints(self):
        out = {}
        for sr in self.sreports:
            sout = sr.all_handlepoints()
            for hp in sout.keys():
                if not (hp in out):
                    out[hp] = []
                out[hp].append(sout[hp])
        return out
        
if __name__ == '__main__':
    tr = TrumpReport("Test Report")
    
    for fakesym in list('ABCDE'):
        sr = SymbolReport(fakesym)
        for fakefeed in list('123'):
            fr = FeedReport(fakefeed)
            rp = ReportPoint("fetched feed", "somecheck", True)
            fr.add_reportpoint(rp)
            rp = ReportPoint("fetched feed", "othercheck", 50)
            fr.add_reportpoint(rp)
        
            try:
                a = b + "a problem"
            except:
                typ, val, tback = sys.exc_info()
                tbextract = trcbm.extract_tb(tback)                
                hp = HandlePointReport("a+b", tbextract)
                fr.add_handlepoint(hp)
            
            rp = ReportPoint("add a and b", "goodcheck", "ab")
            fr.add_reportpoint(rp)
        
            
            try:
                a = 4 + "a problem"
            except:
                typ, val, tback = sys.exc_info()
                tbextract = trcbm.extract_tb(tback)                
                hp = HandlePointReport("4th problem", tbextract)
                fr.add_handlepoint(hp)
            
            sr.add_feedreport(fr)            

        rp = ReportPoint("symbol done", "validwhat", True, pd.DataFrame([1,2,3,4]))
        sr.add_reportpoint(rp)
        
        tr.add_symbolreport(sr)
    
        f = open("C:\\jmclarty\\tr.html",'w+')
        f.write(tr.html)
        f.close()