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
