"""tablesqlite - Declarative SQLite table builder and schema manager.

This package provides classes for defining SQLite table schemas declaratively
and generating SQL DDL statements.
"""

from .query_wrappers import SQLColumnInfo, SQLTableInfo

__all__ = [
    "SQLColumnInfo",
    "SQLTableInfo",
]

__version__ = "0.1.7"
