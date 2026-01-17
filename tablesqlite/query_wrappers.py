"""Query wrapper classes for SQLite table and column operations.

This module provides SQLColumnInfo and SQLTableInfo classes that extend
the base classes with additional query generation capabilities.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from expressql import SQLCondition

from .action_queries import (
    add_column_query,
    create_table_query,
    drop_column_query,
    drop_table_query,
    rename_column_query,
    rename_table_query,
)
from .info_queries import parse_sql_schema
from .objects import (
    SQLColumnInfoBase,
    SQLTableInfoBase,
    Unknown,
    is_undetermined,
    unknown,
)


class SQLColumnInfo(SQLColumnInfoBase):
    """Extended column info class with query generation capabilities.

    This class extends SQLColumnInfoBase to add methods for generating
    SQL statements for column operations like add, drop, and rename.

    Args:
        name: The column name.
        data_type: The SQL data type (e.g., "INTEGER", "TEXT").
        not_null: Whether the column has a NOT NULL constraint.
        default_value: The default value for the column.
        primary_key: Whether the column is a primary key.
        cid: The column ID.
        unique: Whether the column has a UNIQUE constraint.
        foreign_key: Foreign key definition with 'table' and 'column' keys.
        check: CHECK constraint condition.
    """

    def __init__(
        self,
        name: str,
        data_type: str,
        not_null: bool = False,
        default_value: str | int | float | Unknown = unknown,
        primary_key: bool = False,
        cid: int | Unknown = unknown,
        *,
        unique: bool = False,
        foreign_key: dict[str, str] | None = None,
        check: SQLCondition | None = None,
    ) -> None:
        """Initialize a SQLColumnInfo instance."""
        super().__init__(
            name,
            data_type,
            not_null,
            default_value,
            primary_key,
            cid,
            unique=unique,
            foreign_key=foreign_key,
            check=check,
        )

    def _resolve_table_name(
        self,
        table_name: str | None,
        check_in_tables: bool = False,
        solve_by: str = "raise",
    ) -> str | None:
        """Resolve the table name for column operations.

        Args:
            table_name: The table name to use, or None to auto-resolve.
            check_in_tables: Whether to check if the table is linked.
            solve_by: How to handle missing tables: "raise", "ignore", or "none".

        Returns:
            The resolved table name, or None if solve_by is "none".

        Raises:
            ValueError: If table_name is not found and solve_by is "raise".
        """
        if table_name is not None:
            if check_in_tables and table_name not in self.table_names:
                solve_by_lower = solve_by.lower()
                if solve_by_lower == "raise":
                    raise ValueError(
                        f"Table '{table_name}' not found in column's linked tables."
                    )
                elif solve_by_lower == "ignore":
                    return table_name
                elif solve_by_lower == "none":
                    return None
                else:
                    raise ValueError(f"Invalid solve_by value: {solve_by}")
            return table_name

        table_count = len(self._tables)
        if table_count == 1:
            return next(iter(self._tables)).name
        elif table_count > 1:
            raise ValueError(
                "Column is linked to multiple tables. Specify 'table_name'."
            )
        else:
            raise ValueError(
                "Column is not linked to any table. Specify 'table_name'."
            )

    def drop_query(
        self,
        table_name: str | None = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise",
    ) -> tuple[str, list[Any]]:
        """Generate a DROP COLUMN SQL statement.

        Args:
            table_name: The table name, or None to auto-resolve.
            check_if_possible: Whether to check if the column exists.
            check_in_tables: Whether to check if the table is linked.
            solve_by: How to handle missing tables: "raise", "ignore", or "none".

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        resolved_name = self._resolve_table_name(
            table_name, check_in_tables, solve_by
        )
        return drop_column_query(
            resolved_name, self.name, check_if_possible=check_if_possible
        )

    def rename_query(
        self,
        new_name: str,
        table_name: str | None = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise",
    ) -> tuple[str, list[Any]]:
        """Generate a RENAME COLUMN SQL statement.

        Args:
            new_name: The new column name.
            table_name: The table name, or None to auto-resolve.
            check_if_possible: Whether to validate the operation.
            check_in_tables: Whether to check if the table is linked.
            solve_by: How to handle missing tables: "raise", "ignore", or "none".

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        resolved_name = self._resolve_table_name(
            table_name, check_in_tables, solve_by
        )
        return rename_column_query(
            resolved_name, self.name, new_name, check_if_possible=check_if_possible
        )

    def add_query(
        self,
        table_name: str | None = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise",
    ) -> tuple[str, list[Any]]:
        """Generate an ADD COLUMN SQL statement.

        Args:
            table_name: The table name, or None to auto-resolve.
            check_if_possible: Whether to validate the operation.
            check_in_tables: Whether to check if the table is linked.
            solve_by: How to handle missing tables: "raise", "ignore", or "none".

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        resolved_name = self._resolve_table_name(
            table_name, check_in_tables, solve_by
        )
        return add_column_query(
            resolved_name, self, check_if_possible=check_if_possible
        )

    @classmethod
    def from_super(cls, column: SQLColumnInfoBase) -> SQLColumnInfo:
        """Create a SQLColumnInfo from a SQLColumnInfoBase instance.

        Args:
            column: The base column instance to convert.

        Returns:
            A new SQLColumnInfo instance with the same properties.
        """
        return cls(
            name=column.name,
            data_type=column.data_type,
            not_null=column.not_null,
            default_value=column.default_value,
            primary_key=column.primary_key,
            cid=column.cid,
            unique=column.unique,
            foreign_key=column.foreign_key,
            check=column.check,
        )

    @classmethod
    def ensure_subclass(cls, column: SQLColumnInfoBase) -> SQLColumnInfo:
        """Ensure the column is a SQLColumnInfo instance.

        Args:
            column: The column to check or convert.

        Returns:
            The column as a SQLColumnInfo instance.
        """
        if isinstance(column, cls):
            return column
        return cls.from_super(column)


class SQLTableInfo(SQLTableInfoBase):
    """Extended table info class with query generation capabilities.

    This class extends SQLTableInfoBase to add methods for generating
    SQL statements for table operations.

    Args:
        name: The table name.
        columns: Iterable of column definitions.
        database_path: Path to the database file.
        foreign_keys: List of table-level foreign key definitions.
    """

    def __init__(
        self,
        name: str,
        columns: Iterable[SQLColumnInfo] | Unknown = unknown,
        database_path: str | Unknown = unknown,
        foreign_keys: list[dict[str, list[str] | str]] | None = None,
    ) -> None:
        """Initialize a SQLTableInfo instance."""
        super().__init__(name, columns, database_path, foreign_keys)

    def drop_query(self, if_exists: bool = False) -> tuple[str, list[Any]]:
        """Generate a DROP TABLE SQL statement.

        Args:
            if_exists: Whether to include IF EXISTS clause.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return drop_table_query(self, check_if_exists=if_exists)

    def rename_query(
        self, new_name: str, if_exists: bool = False
    ) -> tuple[str, list[Any]]:
        """Generate a RENAME TABLE SQL statement.

        Args:
            new_name: The new table name.
            if_exists: Whether to include IF EXISTS clause.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return rename_table_query(self.name, new_name, check_if_exists=if_exists)

    def create_query(self) -> tuple[str, list[Any]]:
        """Generate a CREATE TABLE SQL statement.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return create_table_query(self)

    def add_column_query(
        self, column: SQLColumnInfoBase, check_if_possible: bool = False
    ) -> tuple[str, list[Any]]:
        """Generate an ADD COLUMN SQL statement.

        Args:
            column: The column to add.
            check_if_possible: Whether to validate the operation.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return add_column_query(self, column, check_if_possible=check_if_possible)

    def drop_column_query(
        self, column_name: str, check_if_possible: bool = False
    ) -> tuple[str, list[Any]]:
        """Generate a DROP COLUMN SQL statement.

        Args:
            column_name: The name of the column to drop.
            check_if_possible: Whether to validate the operation.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return drop_column_query(self, column_name, check_if_possible=check_if_possible)

    def rename_column_query(
        self, old_name: str, new_name: str, check_if_possible: bool = False
    ) -> tuple[str, list[Any]]:
        """Generate a RENAME COLUMN SQL statement.

        Args:
            old_name: The current column name.
            new_name: The new column name.
            check_if_possible: Whether to validate the operation.

        Returns:
            A tuple of (SQL query string, list of parameters).
        """
        return rename_column_query(
            self, old_name, new_name, check_if_possible=check_if_possible
        )

    @classmethod
    def from_super(cls, table: SQLTableInfoBase) -> SQLTableInfo:
        """Create a SQLTableInfo from a SQLTableInfoBase instance.

        Args:
            table: The base table instance to convert.

        Returns:
            A new SQLTableInfo instance with the same properties.
        """
        return cls(
            name=table.name,
            columns=table.columns,
            database_path=table.database_path,
            foreign_keys=table.foreign_keys,
        )

    @classmethod
    def from_sql_schema(
        cls, schema: str | list[dict[str, Any]]
    ) -> SQLTableInfo:
        """Create a SQLTableInfo from a SQL schema string.

        Args:
            schema: SQL CREATE TABLE statement or list of column dictionaries.

        Returns:
            A new SQLTableInfo instance parsed from the schema.
        """
        return cls.from_super(parse_sql_schema(schema))

    def add_column(self, column: SQLColumnInfoBase) -> None:
        """Add a new column to the table.

        Args:
            column: The column to add.

        Raises:
            ValueError: If a column with the same name already exists.
        """
        column = SQLColumnInfo.ensure_subclass(column)
        super().add_column(column)

    def _update_columns(self, new_columns: list[SQLColumnInfoBase]) -> None:
        """Update internal state with new column list.

        Handles _tables linkage and dictionary sync.

        Args:
            new_columns: The new list of columns.
        """
        old_columns = {col.name: col for col in self.columns}
        new_column_names = {col.name for col in new_columns}

        # Remove unlinked columns
        for name, column in old_columns.items():
            if name not in new_column_names:
                column._tables.discard(self)
                self._column_dict.pop(name, None)

        # Add new ones
        for column in new_columns:
            self.validate_new_column(column)
            self._column_dict[column.name] = column
            column._tables.add(self)

        self._columns = new_columns

    @staticmethod
    def validate_columns(
        columns: Iterable[SQLColumnInfoBase] | Unknown,
    ) -> list[SQLColumnInfo]:
        """Validate and convert columns to SQLColumnInfo instances.

        Args:
            columns: Iterable of column definitions.

        Returns:
            List of validated SQLColumnInfo instances.
        """
        if is_undetermined(columns):
            return []
        validated_columns = SQLTableInfoBase.validate_columns(columns)
        actual_columns = [
            SQLColumnInfo.ensure_subclass(col) for col in validated_columns
        ]
        return actual_columns

