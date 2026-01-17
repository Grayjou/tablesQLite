"""Table information query utilities.

This module provides functions for generating queries to retrieve
table information from SQLite databases.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..validation import validate_name


def validate_table_name(
    table_name_pos: int = 0,
    already_validated_pos: int | None = None,
) -> Callable:
    """Decorator to validate table names in function arguments.

    Args:
        table_name_pos: Position of the table name argument.
        already_validated_pos: Position of the already_validated flag argument.

    Returns:
        A decorator function.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            table_name = kwargs.get("table_name")
            if table_name is None and len(args) > table_name_pos:
                table_name = args[table_name_pos]

            already_validated = kwargs.get("already_validated", False)
            if already_validated_pos is not None and len(args) > already_validated_pos:
                arg_value = args[already_validated_pos]
                if isinstance(arg_value, bool):
                    already_validated = arg_value

            if not already_validated:
                validate_name(table_name, allow_dot=False)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_all_tables_query() -> tuple[str, list[Any]]:
    """Get a SQL query to retrieve all table names from the database.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    return "SELECT name FROM sqlite_master WHERE type='table'", []


@validate_table_name(0, 1)
def get_table_info_query(
    table_name: str,
    already_validated: bool = False,
) -> tuple[str, list[Any]]:
    """Get a SQL query to retrieve table information.

    Args:
        table_name: The name of the table to get information for.
        already_validated: Whether the table name has been validated.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    return f"PRAGMA table_info('{table_name}')", []


@validate_table_name(0, 1)
def count_rows_query(
    table_name: str,
    already_validated: bool = False,
) -> tuple[str, list[Any]]:
    """Get a SQL query to count rows in a table.

    Args:
        table_name: The name of the table to count rows for.
        already_validated: Whether the table name has been validated.

    Returns:
        A tuple of (SQL query string, list of parameters).
    """
    return f"SELECT COUNT(*) FROM '{table_name}'", []
