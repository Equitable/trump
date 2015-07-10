
from sqlalchemy import Column, MetaData, Integer, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ENGINE_STR = "sqlite:///"
engine = create_engine(ENGINE_STR, echo=False)

Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

metadata = MetaData(bind=engine)

from trump.tools.reprobj import ReprObjType

class ReprObjExample(Base):
    __tablename__ = 'reprobjex'
    
    idcol = Column('idcol', Integer, primary_key=True)
    excol = Column('excol', ReprObjType)

Base.metadata.create_all(engine)

import datetime as dt

class TestReprObj(object):
    def test_check_reprobjs(self):
        for tobj in [1, 2.0, 'three', dt.date(2014, 1, 1)]:
            ttyp = type(tobj)
            
            roe = ReprObjExample(excol=tobj)
            
            session.add(roe)
            session.commit()
            
            lastid = session.query(func.max(ReprObjExample.idcol).label('lastid')).one()[0]
            results = session.query(ReprObjExample).filter(ReprObjExample.idcol == lastid).all()[0]
            
            assert results.excol == tobj
            assert type(results.excol) == ttyp
            
            session.delete(roe)
            session.commit()
