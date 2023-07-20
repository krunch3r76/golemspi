import sqlite3
from .database_types import register_database_types

register_database_types()


# Create an in-memory SQLite database connection
connection = sqlite3.connect(":memory:")
connection.isolation_level = None

from .tables import create_tables

create_tables()

# __all__ = ["connection"]
