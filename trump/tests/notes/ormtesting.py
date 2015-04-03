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




### Testing the Handle mutability

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

###################################################
# test tagging of a symbol from first principles

    asymbol = Symbol("testsymbol","testdescription","T","tst","PRIORITY_FILL")
    session.add(asymbol)


    atag1 = SymbolTag("testag1")
    asymbol.tags = [atag1]

    asymbol.tags.append(SymbolTag("testag2"))

    atag3 = SymbolTag("testag3",asymbol)
    session.add(atag3)

    atag4 = SymbolTag("testag4",asymbol.name)
    session.add(atag4)

    session.commit()

    try:
        atag5 = SymbolTag("testag5")
        session.add(atag5)
        session.commit()
    except IntegrityError:
        session.rollback()

    atag5.symname = asymbol.name
    session.add(atag5)
    session.commit()

    asymbol.add_tags("testag6")

    asymbol.add_tags(['testag7','testag8'])

    asymbol.del_tags("testag1")

    asymbol.del_tags(["testag2","testag3"])

    session.close()

###################################################
# test that tag searching is working...

    sm = SymbolManager()

    sm.create('symone').add_tags(['alpha', 'beta', 'charlie', 'echo'])
    sm.create('symtwo').add_tags(['alpha', 'charlie', 'delta', 'echofoxtrot'])
    sm.create('symthr').add_tags(['alpha', 'beta', 'foxtrotecho'])

    for crit in ("charlie", "echo", "%echo%", "%echo"):
        syms = sm.search_tag(crit)
        print "\nSeaching for {}".format(crit)
        for sym in syms:
            print sym.name


    sm.finish()
