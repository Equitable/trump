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

class ProxyDict(object):
    def __init__(self, parent, collection_name, childclass, keyname, valuename='value'):
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

    def __call__(self,valuename=None):
        keys = self.keys()
        val = valuename or self.valuename
        values = [getattr(self[k],val) for k in keys]
        d = dict(zip(keys,values))
        return d
        
    def __getitem__(self, key):
        x = self.collection.filter_by(**{self.keyname:key}).first()
        
        if x:
            return x
        else:
            raise KeyError(key)

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
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
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


def isinstanceofany(obj,typs):
    return any([isinstance(obj,t) for t in typs])
    