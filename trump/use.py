# -*- coding: utf-8 -*-
"""
Created on Mon Jan 05 22:03:38 2015

@author: Jeffrey
"""

from orm import session, Symbol, Override

from sqlalchemy.sql.expression import insert, update, delete, select

from sqlalchemy import func

from sqlalchemy.sql import and_

syms = session.query(Symbol).filter(Symbol.name.like("oil%")).all()

eu_oil = syms[1]

df = eu_oil.cache()

    


#s = select([Override.dt_ind,Override.value]).where(Override.symname == 'oil_CONT').execute()


#gb = session.query(Override.dt_ind,func.max(Override.dt_log).label('max_dt_log')).group_by(Override.dt_ind).subquery()

#ors = session.query(Override).join((gb, and_(Override.dt_ind == gb.c.dt_ind, Override.dt_log == gb.c.max_dt_log))).all()
#s = select([])
#res = session.query(Override).filter(Override.symname == 'oil_CONT').all()


#print eu_oil.data()

#f = eu_oil.feeds[0]
