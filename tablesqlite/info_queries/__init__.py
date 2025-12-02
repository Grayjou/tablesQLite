"""Info queries module for SQL schema parsing.

This module exports functions for parsing SQL schemas and retrieving
table information.
"""

from .schema_parse import parse_sql_schema

__all__ = [
    "parse_sql_schema",
]
