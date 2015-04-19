"""
Creates the ReprObjType object, which enables any python object to be stored
as a string in a database.
"""

from sqlalchemy.types import TypeDecorator, String

class ReprObjType(TypeDecorator):

    """ 
    SQLAlchemy type definition for the ReprObj implementation.
    A ReprObj is a python object that enables lazily storing
    flags into a single integer value for quick database access and use."""

    impl = String
    
    def __init__(self, *args, **kwargs):
        super(ReprObjType, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """
        When SQLAlchemy binds a ReprObjType, it converts it
        to a string for storage in the database, via the python
        repr string equivalent.
        """
        if value is not None:
            value = repr(value)
        return value

    def process_result_value(self, value, dialect):
        """
        When SQLAlchemy gets the string representation from a ReprObjType
        column, it converts it to the python equivalent via exec.
        """
        if value is not None:
            exec("value = " + value)
        return value

    def copy(self):
        return ReprObjType()

