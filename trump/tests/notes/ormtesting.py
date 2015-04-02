# -*- coding: utf-8 -*-


 for x in range(3):
     un = str(x) + dt.datetime.now().strftime("%H%M%S")

     NewSymbol = Symbol(name="NewSymbol" + un)

     NewSymbol.description = 'tester chester 2 ' + un
     NewSymbol.freq = 'D'
     NewSymbol.units = '$'

     # Nice to have:
     # NewSymbol.tags = ['Alpha', 'Beta', 'Charlie', 'Delta']
     NewSymbol.add_tag("Alpha")
     NewSymbol.add_tags(["Beta", "Charlie", "Delta"])

     NewSymbol.add_alias("Newish")
     NewSymbol.add_alias("Newer")

     SESSION.commit()

     nota = {'checkpoint': 'Exception', 'logic': 'NoData'}
     notac = {'checkpoint': 'Check', 'logic': 'NoData'}
     egsourcing = {'stype': 'DBNonAPICompliant',
                   'db': 'General',
                   'user': 'chester'}
     for f in range(4):
         un = str(x) + dt.datetime.now().strftime("%H%M%S")
         NewFeed = Feed(NewSymbol, "DB",
                        sourcing=egsourcing)
         SESSION.add(NewFeed)
     NewSymbol._init_datatable()
     SESSION.commit()
 SESSION.commit()
 mysymbol = SESSION.query(Symbol).all()[-1]






###########################3333

    sm = SymbolManager()

    print "Getting Oil"

    oil = sm.create('oil')

    print oil

    from copy import copy

    print "The session should be clean:"
    print sm.ses.dirty
    #oil.handle.egint = 10
    #print sm.ses.dirty

    #print oil.handle.caching_of_feeds
    #print oil.handle

    #oil.handle.egint = 55
    #modify
    #oil.handle.caching_of_feeds = BitFlag(34)

    print oil.handle.caching_of_feeds
    print oil.handle.caching_of_feeds.val
    print oil.handle

    #print "The id of caching_of_feeds is {}".format(id(oil.handle.caching_of_feeds))
    oil.handle.caching_of_feeds['txtlog'] = True
    oil.handle.caching_of_feeds['txtlog'] = False
    #print "The id of caching_of_feeds is {}".format(id(oil.handle.caching_of_feeds))
    #oil.handle.caching_of_feeds = copy(oil.handle.caching_of_feeds)
    #print "The id of caching_of_feeds is {}".format(id(oil.handle.caching_of_feeds))

    #oil.handle.egint = 56

    print oil.handle.caching_of_feeds
    print oil.handle.caching_of_feeds.val
    print oil.handle

    #print oil.handle.caching_of_feeds
    print sm.ses.dirty

    #print oil.handle

    sm.complete()

    print sm.ses.dirty
    sm.finish()
