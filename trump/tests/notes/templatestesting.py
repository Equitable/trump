 if True:
     EGF = fMyTable('atable')
     print EGF.sourcing
     print EGF.meta

     EGF = fEcon('SP500')
     print EGF.sourcing
     print EGF.meta

     EGF = fSQL('SELECT t,data FROM math ORDER BY t;')
     print EGF.sourcing
     print EGF.meta

     EGF = fYahooFinance('TSLA')
     print EGF.sourcing
     print EGF.meta

     EGF = fGoogleFinance('TSLA')
     print EGF.sourcing
     print EGF.meta

     EGF = fStLouisFED('GDP')
     print EGF.sourcing
     print EGF.meta

 if True:
     EGM = mRollingMean(window=5, min_periods=4, center=True)
     for akey in EGM.as_odict.keys():
         print akey
         for ins in EGM.as_odict[akey]:
             print " ", EGM.as_odict[akey][ins]

     EGM = mSimpleExample(3, 5)
     for akey in EGM.as_odict.keys():
         print akey
         for ins in EGM.as_odict[akey]:
             print " ", EGM.as_odict[akey][ins]