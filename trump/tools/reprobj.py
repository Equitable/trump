"""
Creates the ReprObjType object, which enables any python object to be stored
as a string in a database.

In order for Trump to support it, reprobj.py needs to be able to run
an exec command, of the object's repr, successfully.  So, extra
import statements may be needed and added in such a way that the import
statement matches the object's repr.
"""

from sqlalchemy.types import TypeDecorator, String

# Wrap any needed third-party libraries or modules, in a try-pass statetment.
# to ensure any other users, stay sane.  Example was done with the 
# datetime, which obviously all users have.

try: import datetime
except: pass


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
            cmd = "value = {}".format(value)
            exec(cmd)
        return value

    def copy(self):
        return ReprObjType()

