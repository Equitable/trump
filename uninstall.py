from trump.orm import create_engine, engine_str

def UninstallTrump(RemoveDataTables=True, RemoveOverrides=True, RemoveFailsafes=True):
    """
    This script removes all tables associated with Trump.
    
    It's written for PostgreSQL, but should be very easy to adapt to other
    databases.
    """
    
    ts = ['_symbols', '_symbol_validity', '_symbol_tags', '_symbol_aliases', 
          '_feeds', '_feed_munging', '_feed_munging_args', '_feed_sourcing', 
          '_feed_validity', '_feed_meta', '_feed_tags']
    
    if RemoveOverrides:
        ts.append('_overrides')
        
    if RemoveFailsafes:
        ts.append('_failsafes')

    engine = create_engine(engine_str)
       
    if RemoveDataTables:
        results = engine.execute("SELECT name FROM _symbols;")
        datatables = [row['name'] for row in results]
        ts = ts + datatables
    
    drops = "".join(['DROP TABLE IF EXISTS "{}" CASCADE;'.format(t) for t in ts])
    
    engine.execute(drops)

if __name__ == "__main__":
    UninstallTrump()