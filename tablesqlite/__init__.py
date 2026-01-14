"""tablesqlite - Declarative SQLite table builder and schema manager.

This package provides classes for defining SQLite table schemas declaratively
and generating SQL DDL statements.
"""

from .query_wrappers import SQLColumnInfo, SQLTableInfo
from .utils import convert_enum_value, generate_migration, validate_foreign_keys

__all__ = [
    "SQLColumnInfo",
    "SQLTableInfo",
    "convert_enum_value",
    "validate_foreign_keys",
    "generate_migration",
]

__version__ = "0.1.8"
