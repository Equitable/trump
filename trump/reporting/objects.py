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

class HandlePointReport(object):
    def __init__(self, handlepoint, trace):
        self.hpoint = handlepoint
        self.trace = trace
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
    def html(self):
        return "{} {} {}\n{}".format(self.rpoint, self.attribute, self.value,
                                    self.extended)

class FeedReport(object):
    def __init__(self, num):
        self.num = num
        self.tstamp = dt.datetime.now() 
        self.handlepoints = []
        self.reportpoints = []
    def add_handlepoint(self, hpreport):
        self.handlepoints.append(hpreport)
    def add_reportpoint(self, rpoint):
        self.reportpoints.append(rpoint)
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
    def add_feedreport(self, freport):
        self.freports.append(freport)
    def add_handlepoint(self, hpreport):
        self.handlepoints.append(hpreport)
    def add_reportpoint(self, rpoint):
        self.reportpoints.append(rpoint)
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
    def html(self):
        
        thtml = []
        
        thtml.append("<h1>{}</h1>".format(self.name))
        
        for sr in self.sreports:
            thtml.append(sr.html)
            thtml.append("<br>")
            
        return "".join(thtml)

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