"""Column operation queries for ALTER TABLE statements.

This module provides functions for generating SQL statements for
column operations like add, drop, and rename.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..objects import SQLColumnInfoBase, SQLTableInfoBase
from ..objects.generic import ensure_quoted


def _extract_table_name(
    table: str | SQLTableInfoBase,
    check: Callable[[SQLTableInfoBase], None] | None = None,
) -> str:
    """Extract the table name from a string or SQLTableInfoBase.

    Args:
        table: The table name as a string or SQLTableInfoBase instance.
        check: Optional callback to validate the table object.

    Returns:
        The extracted table name.

    Raises:
        TypeError: If table is not a string or SQLTableInfoBase.
    """
    if not isinstance(table, (str, SQLTableInfoBase)):
        raise TypeError("table must be a string or an instance of SQLTableInfoBase")
    if isinstance(table, SQLTableInfoBase):
        if check:
            check(table)
        return table.name
    return table.strip('"').strip("'")


def add_column_query(
    table: SQLTableInfoBase | str,
    column: SQLColumnInfoBase,
    check_if_possible: bool = False,
) -> tuple[str, list[Any]]:
    """Generate an ALTER TABLE ADD COLUMN SQL statement.

    Args:
        table: The table to add the column to.
        column: The column to add.
        check_if_possible: Whether to validate that the column can be added.

    Returns:
        A tuple of (SQL query string, list of parameters).

    Raises:
        TypeError: If column is not a SQLColumnInfoBase instance.
    """
    if not isinstance(column, SQLColumnInfoBase):
        raise TypeError("column must be an instance of SQLColumnInfoBase")

    def check(table_obj: SQLTableInfoBase) -> None:
        if check_if_possible:
            table_obj.validate_new_column(column)

    table_name = _extract_table_name(table, check)
    query = (
        f"ALTER TABLE {ensure_quoted(table_name)} "
        f"ADD COLUMN {column.creation_str()}"
    )
    return query, []


def drop_column_query(
    table: SQLTableInfoBase | str,
    column_name: str,
    check_if_possible: bool = False,
) -> tuple[str, list[Any]]:
    """Generate an ALTER TABLE DROP COLUMN SQL statement.

    Args:
        table: The table to drop the column from.
        column_name: The name of the column to drop.
        check_if_possible: Whether to validate that the column exists.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """

    def check(table_obj: SQLTableInfoBase) -> None:
        if check_if_possible and column_name not in table_obj.column_dict:
            raise ValueError(
                f"Column '{column_name}' does not exist in table '{table_obj.name}'"
            )

    table_name = _extract_table_name(table, check)
    query = (
        f"ALTER TABLE {ensure_quoted(table_name)} "
        f"DROP COLUMN {ensure_quoted(column_name)}"
    )
    return query, []


def rename_column_query(
    table: SQLTableInfoBase | str,
    old_name: str,
    new_name: str,
    check_if_possible: bool = False,
) -> tuple[str, list[Any]]:
    """Generate an ALTER TABLE RENAME COLUMN SQL statement.

    Args:
        table: The table containing the column.
        old_name: The current column name.
        new_name: The new column name.
        check_if_possible: Whether to validate the rename operation.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """

    def check(table_obj: SQLTableInfoBase) -> None:
        if not check_if_possible:
            return
        if old_name not in table_obj.column_dict:
            raise ValueError(
                f"Column '{old_name}' does not exist in table '{table_obj.name}'"
            )
        if new_name in table_obj.column_dict:
            raise ValueError(
                f"Column '{new_name}' already exists in table '{table_obj.name}'"
            )

    table_name = _extract_table_name(table, check)
    query = (
        f"ALTER TABLE {ensure_quoted(table_name)} "
        f"RENAME COLUMN {ensure_quoted(old_name)} TO {ensure_quoted(new_name)}"
    )
    return query, []

