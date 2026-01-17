"""Utility functions for tablesqlite.

This module provides helper functions for type conversion, foreign key validation,
and schema comparison operations.
"""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tablesqlite import SQLTableInfo


def convert_enum_value(value: Any, enum_class: type[IntEnum]) -> IntEnum:
    """Convert a value to an IntEnum, handling string and int inputs.

    Args:
        value: The value to convert (can be str, int, or IntEnum)
        enum_class: The IntEnum class to convert to

    Returns:
        The IntEnum value

    Raises:
        TypeError: If enum_class is not an IntEnum subclass
        ValueError: If the value cannot be converted to the enum

    Examples:
        >>> from enum import IntEnum
        >>> class Status(IntEnum):
        ...     PENDING = 1
        ...     ACTIVE = 2
        >>> convert_enum_value(1, Status)
        <Status.PENDING: 1>
        >>> convert_enum_value("2", Status)
        <Status.ACTIVE: 2>
        >>> convert_enum_value(Status.ACTIVE, Status)
        <Status.ACTIVE: 2>
    """
    if not issubclass(enum_class, IntEnum):
        msg = f"enum_class must be an IntEnum subclass, got {type(enum_class)}"
        raise TypeError(msg)

    if isinstance(value, enum_class):
        return value

    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError as e:
            msg = (
                f"Cannot convert string '{value}' to int "
                f"for enum {enum_class.__name__}"
            )
            raise ValueError(msg) from e

    try:
        return enum_class(value)
    except ValueError as e:
        raise ValueError(
            f"Value {value} is not a valid {enum_class.__name__}"
        ) from e


def validate_foreign_keys(
    table: SQLTableInfo,
    available_tables: dict[str, SQLTableInfo],
) -> list[str]:
    """Validate that all foreign key references point to existing tables.

    This function checks both inline foreign keys (defined at the column level)
    and table-level foreign keys to ensure they reference tables that exist
    in the available_tables dictionary.

    Args:
        table: The SQLTableInfo object to validate
        available_tables: Dictionary mapping table names to SQLTableInfo objects

    Returns:
        List of validation errors (empty if valid)

    Examples:
        >>> from tablesqlite import SQLTableInfo, SQLColumnInfo
        >>> users = SQLTableInfo(
        ...     "users",
        ...     [SQLColumnInfo("id", "INTEGER", primary_key=True)]
        ... )
        >>> posts = SQLTableInfo("posts", [
        ...     SQLColumnInfo("id", "INTEGER", primary_key=True),
        ...     SQLColumnInfo(
        ...         "user_id", "INTEGER",
        ...         foreign_key={"table": "users", "column": "id"}
        ...     )
        ... ])
        >>> tables = {"users": users, "posts": posts}
        >>> validate_foreign_keys(posts, tables)
        []
        >>> # Missing users table
        >>> validate_foreign_keys(posts, {"posts": posts})
        ["Foreign key in column 'user_id' references unknown table: users"]
    """
    errors = []

    # Check inline foreign keys from columns
    for col in table.columns:
        if col.foreign_key:
            ref_table = col.foreign_key.get('table')
            if ref_table and ref_table not in available_tables:
                msg = (
                    f"Foreign key in column '{col.name}' "
                    f"references unknown table: {ref_table}"
                )
                errors.append(msg)

    # Check table-level foreign keys
    for fk in table.foreign_keys:
        ref_table = fk.get('ref_table')
        if ref_table and ref_table not in available_tables:
            errors.append(
                f"Foreign key references unknown table: {ref_table}"
            )

    return errors


def generate_migration(
    old_table: SQLTableInfo,
    new_table: SQLTableInfo,
) -> list[tuple[str, list[Any]]]:
    """Generate SQL statements to migrate from old_table to new_table.

    This function compares two SQLTableInfo objects and generates ALTER TABLE
    statements to transform the old schema into the new one. Due to SQLite
    limitations, some operations are not fully supported.

    SQLite Limitations:
    - Cannot DROP COLUMN in older SQLite versions (< 3.35.0)
    - Cannot modify existing columns (change type, constraints, etc.)
    - Cannot add constraints to existing tables except via table recreation
    - Cannot drop/modify PRIMARY KEY or UNIQUE constraints

    For complex migrations, consider using the table recreation pattern:
    1. CREATE new table with updated schema
    2. COPY data from old to new
    3. DROP old table
    4. RENAME new table to old name

    Args:
        old_table: The original SQLTableInfo object
        new_table: The target SQLTableInfo object

    Returns:
        List of (sql, params) tuples to execute in order

    Examples:
        >>> from tablesqlite import SQLTableInfo, SQLColumnInfo
        >>> old = SQLTableInfo("users", [
        ...     SQLColumnInfo("id", "INTEGER", primary_key=True),
        ...     SQLColumnInfo("name", "TEXT")
        ... ])
        >>> new = SQLTableInfo("users", [
        ...     SQLColumnInfo("id", "INTEGER", primary_key=True),
        ...     SQLColumnInfo("name", "TEXT"),
        ...     SQLColumnInfo("email", "TEXT")
        ... ])
        >>> migrations = generate_migration(old, new)
        >>> print(migrations[0][0])
        ALTER TABLE "users" ADD COLUMN "email" TEXT
    """
    from .objects.generic import ensure_quoted

    migrations: list[tuple[str, list[Any]]] = []

    # Check if table names match
    if old_table.name != new_table.name:
        # Table rename
        sql = (
            f'ALTER TABLE {ensure_quoted(old_table.name)} '
            f'RENAME TO {ensure_quoted(new_table.name)}'
        )
        migrations.append((sql, []))

    # Get column dictionaries for comparison
    old_cols = {col.name: col for col in old_table.columns}
    new_cols = {col.name: col for col in new_table.columns}

    # Find added columns
    added_cols = set(new_cols.keys()) - set(old_cols.keys())
    for col_name in sorted(added_cols):
        col = new_cols[col_name]
        # Generate ADD COLUMN statement
        col_def = col.creation_str()
        sql = (
            f'ALTER TABLE {ensure_quoted(new_table.name)} '
            f'ADD COLUMN {col_def}'
        )
        migrations.append((sql, []))

    # Find removed columns - note SQLite limitations
    removed_cols = set(old_cols.keys()) - set(new_cols.keys())
    if removed_cols:
        for col_name in sorted(removed_cols):
            # SQLite 3.35.0+ supports DROP COLUMN
            sql = (
                f'-- SQLite 3.35.0+ required: '
                f'ALTER TABLE {ensure_quoted(new_table.name)} '
                f'DROP COLUMN {ensure_quoted(col_name)}'
            )
            migrations.append((sql, []))

    # Find modified columns - SQLite doesn't support ALTER COLUMN
    common_cols = set(old_cols.keys()) & set(new_cols.keys())
    for col_name in sorted(common_cols):
        old_col = old_cols[col_name]
        new_col = new_cols[col_name]

        # Check if column definition changed
        if old_col.to_dict() != new_col.to_dict():
            # SQLite doesn't support modifying columns directly
            sql = (
                f'-- Cannot modify column {ensure_quoted(col_name)} '
                f'directly in SQLite. Consider table recreation pattern.'
            )
            migrations.append((sql, []))

    # Check for foreign key changes
    old_fks = {str(fk) for fk in old_table.foreign_keys}
    new_fks = {str(fk) for fk in new_table.foreign_keys}

    if old_fks != new_fks:
        migrations.append((
            '-- Foreign key changes require table recreation in SQLite.',
            []
        ))

    return migrations
