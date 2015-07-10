from trump.reporting.objects import *

class TestReportingObjects(object):

    def test_html_creation(self):

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

            try:
                a = int("problem")
            except:
                typ, val, tback = sys.exc_info()
                tbextract = trcbm.extract_tb(tback)                
                hp = HandlePointReport("4th problem", tbextract)
                sr.add_handlepoint(hp)
                    
            rp = ReportPoint("symbol done", "validwhat", True, pd.DataFrame([1,2,3,4]))
            sr.add_reportpoint(rp)
            
            tr.add_symbolreport(sr)
        
            print tr.html


        