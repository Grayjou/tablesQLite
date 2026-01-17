"""Table operation queries for DDL statements.

This module provides functions for generating SQL statements for
table operations like create, drop, and rename.
"""

from __future__ import annotations

from typing import Any

from ..objects import SQLTableInfoBase


def _extract_table_name(table: str | SQLTableInfoBase) -> str:
    """Extract the table name from a string or SQLTableInfoBase.

    Args:
        table: The table name as a string or SQLTableInfoBase instance.

    Returns:
        The extracted table name.

    Raises:
        TypeError: If table is not a string or SQLTableInfoBase.
    """
    if not isinstance(table, (str, SQLTableInfoBase)):
        raise TypeError("table must be a string or an instance of SQLTableInfoBase")
    if isinstance(table, SQLTableInfoBase):
        return table.name
    return table.strip('"').strip("'")


def create_table_query(t: SQLTableInfoBase) -> tuple[str, list[Any]]:
    """Generate a CREATE TABLE SQL statement.

    Args:
        t: The table to create.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    return t.creation_str(), []


def drop_table_query(
    table: SQLTableInfoBase | str,
    check_if_exists: bool = False,
) -> tuple[str, list[Any]]:
    """Generate a DROP TABLE SQL statement.

    Args:
        table: The table to drop.
        check_if_exists: Whether to include IF EXISTS clause.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    table_name = _extract_table_name(table)
    if check_if_exists:
        query = f"DROP TABLE IF EXISTS {table_name}"
    else:
        query = f"DROP TABLE {table_name}"
    return query, []


def rename_table_query(
    old_name: str,
    new_name: str,
    check_if_exists: bool = False,
) -> tuple[str, list[Any]]:
    """Generate an ALTER TABLE RENAME SQL statement.

    Args:
        old_name: The current table name.
        new_name: The new table name.
        check_if_exists: Whether to include IF EXISTS clause.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    if check_if_exists:
        query = f"ALTER TABLE IF EXISTS {old_name} RENAME TO {new_name}"
    else:
        query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
    return query, []
