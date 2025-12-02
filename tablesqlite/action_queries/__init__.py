"""Action queries module for table and column DDL operations.

This module exports functions for generating ALTER TABLE and other
DDL statements for table and column operations.
"""

from .columns import (
    add_column_query,
    drop_column_query,
    rename_column_query,
)
from .tables import (
    create_table_query,
    drop_table_query,
    rename_table_query,
)

__all__ = [
    "add_column_query",
    "drop_column_query",
    "rename_column_query",
    "create_table_query",
    "drop_table_query",
    "rename_table_query",
]
