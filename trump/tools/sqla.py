###############################################################################
#
# PyLint tests that will never be applied by Trump.
#
# Used * or ** magic, we're not getting rid of this, it's imperative to Trump.
# pylint: disable-msg=W0142

# Too many/few arguments, ignored, because its confusing and doesn't make
#                         sense to refactor this stuff in this module.
#
# pylint: disable-msg=R0913
# pylint: disable-msg=R0903
#
# Redefining built-in
#


"""
SQLAlchemy mixins used to implement standard repr, proxy objects
"""
import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.dynamic import AppenderQuery

class ReprMixin(object):

    """Hooks into SQLAlchemy's magic to make repr work."""

    def __repr__(self):
        def reprs():
            for col in self.__table__.c:
                yield col.name, repr(getattr(self, col.name))

        def format(seq):
            for key, value in seq:
                yield '%s=%s' % (key, value)

        args = '(%s)' % ', '.join(format(reprs()))
        classy = type(self).__name__
        return classy + args

class DuckTypeMixin(object):
    def setval(self, val):
        self.set_all_to_none()
        
        if val is None:
            colsw = 0
        elif isinstance(val, bool):
            colsw = 1
            self.boolcol = val
        elif isinstance(val, (str, unicode)):
            colsw = 2
            self.strcol = val
        elif isinstance(val, int):
            colsw = 3
            self.intcol = val
        elif isinstance(val, float):
            colsw = 4
            self.floatcol = val
        else:
            colsw = 5
            self.reprcol = val
        
        self._colswitch = colsw
    @property
    def val(self):

        colsw = self._colswitch
        
        if colsw == 0:
            return None
        elif colsw == 1:
            return self.boolcol
        elif colsw == 2:
            return self.strcol
        elif colsw == 3:
            return self.intcol
        elif colsw == 4:
            return self.floatcol
        elif colsw == 5:
            return self.reprcol
        raise Exception("Unknown column switch {}".format(colsw))

    def set_all_to_none(self):
        self.boolcol = None
        self.strcol = None
        self.intcol = None
        self.floatcol = None
        self.reprcol = None
        
class ProxyDict(object):

    """ implements a SQLA object methods required for dict-like usage"""

    def __init__(self, parent, collection_name, childclass, keyname,
                 valuename='value'):
        self.parent = parent
        self.collection_name = collection_name
        self.childclass = childclass
        self.keyname = keyname
        self.valuename = valuename

    @property
    def collection(self):
        return getattr(self.parent, self.collection_name)

    def keys(self):
        descriptor = getattr(self.childclass, self.keyname)
        return [x[0] for x in self.collection.values(descriptor)]

    def __call__(self, valuename=None):
        keys = self.keys()
        val = valuename or self.valuename
        values = [getattr(self[k], val) for k in keys]
        return dict(zip(keys, values))

    def __getitem__(self, key):
        itm = self.collection.filter_by(**{self.keyname: key}).first()

        if itm:
            return itm
        else:
            raise KeyError(key)
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __setitem__(self, key, value):
        try:
            existing = self[key]
            self.collection.remove(existing)
        except KeyError:
            pass
        self.collection.append(value)


def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            qry = session.query(cls)
            qry = queryfunc(qry, *arg, **kw)
            obj = qry.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj


def unique_constructor(scoped_session, hashfunc, queryfunc):
    def decorate(cls):
        def _null_init(self, *arg, **kw):
            pass

        def __new__(cls, bases, *arg, **kw):
            # no-op __new__(), called
            # by the loading procedure
            if not arg and not kw:
                return object.__new__(cls)

            session = scoped_session()

            def constructor(*arg, **kw):
                obj = object.__new__(cls)
                obj._init(*arg, **kw)
                return obj

            return _unique(
                session,
                cls,
                hashfunc,
                queryfunc,
                constructor,
                arg, kw
            )

        # note: cls must be already mapped for this part to work
        cls._init = cls.__init__
        cls.__init__ = _null_init
        cls.__new__ = classmethod(__new__)
        return cls

    return decorate


def isinstanceofany(obj, typs):
    return any([isinstance(obj, t) for t in typs])

def new_alchemy_encoder():
    _visited_objs = []
    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_')]:
                    if field in ('name','description','units'):
                        fields[field] = obj.__getattribute__(field)
                    elif field in ('meta',):
                        metas = obj.__getattribute__(field).all()
                        fields[field] = {meta.attr : meta.value for meta in metas}
                    elif field in ('tags',):
                        tags = obj.__getattribute__(field)
                        fields[field] = [tag.tag for tag in tags]
                        
                    #elif field in ('feeds',):
                    #    fields[field] = obj.__getattribute__(field)
                    #elif field in ('sourcing', 'sourcekwargs'):
                    #    sources = obj.__getattribute__(field).all()
                    #    fields[field] = repr(sources)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder