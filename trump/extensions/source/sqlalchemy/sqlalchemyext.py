
stype = 'SQLAlchemy'
renew = True

class Source(object):
    def __init__(self, ses, **kwargs):
        NotImplementedError("SQLAlchemy")

    def getseries(self, ses, **kwargs):
        NotImplementedError("SQLAlchemy")

        return data
