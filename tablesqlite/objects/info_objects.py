"""Base classes for SQL table and column information.

This module provides SQLColumnInfoBase and SQLTableInfoBase classes that
represent metadata for SQL columns and tables with support for various
constraints like NOT NULL, DEFAULT, CHECK, UNIQUE, PRIMARY KEY, and FOREIGN KEY.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Union

from expressql import SQLCondition, SQLExpression, col

from ..validation import (
    DualContainer,
    UndeterminedContainer,
    add_bool_properties,
    add_undetermined_properties,
    ensure_all_bools,
    upper_before_bracket,
    validate_data_type,
    validate_database_path,
    validate_name,
)
from .generic import Unknown, ensure_quoted, is_undetermined, unknown

SQL_LITERAL_DEFAULTS = {
    "CURRENT_TIME",
    "CURRENT_DATE",
    "CURRENT_TIMESTAMP",
    "NULL",
}


def autoconvert_default(
    value: str | int | float | bool | Unknown | SQLExpression,
) -> str | int | float | bool | Unknown | SQLExpression:
    """Convert SQL literal defaults to SQLExpression objects.

    Args:
        value: The value to potentially convert.

    Returns:
        The converted value, or the original if no conversion needed.
    """
    if isinstance(value, str) and value.upper() in SQL_LITERAL_DEFAULTS:
        return col(value.upper())
    return value


def get_value(
    item: str | int | float | SQLExpression | Unknown,
) -> str | int | float | Unknown:
    """Extract the value from an item, handling Unknown and SQLExpression.

    Args:
        item: The item to extract the value from.

    Returns:
        The extracted value, or unknown if the item is Unknown.
    """
    if isinstance(item, Unknown):
        return unknown
    elif isinstance(item, SQLExpression):
        return item.true_value()
    return item


def format_default_value(val: str | int | float | SQLExpression) -> str:
    """Format a default value for use in SQL.

    Args:
        val: The value to format.

    Returns:
        The formatted value as a string.
    """
    if isinstance(val, SQLExpression):
        return val.sql_string()
    elif isinstance(val, str):
        return f"'{val}'"
    else:
        return str(val)



@add_bool_properties("not_null", "primary_key", "unique")
@add_undetermined_properties(
    cid=int, default_value=Union[str, int, float, SQLExpression]
)
class SQLColumnInfoBase(DualContainer):
    """Base class representing metadata for a SQL column.

    This class provides comprehensive support for SQL column constraints
    including NOT NULL, DEFAULT, CHECK, UNIQUE, PRIMARY KEY, and FOREIGN KEY.

    Args:
        name: The column name.
        data_type: The SQL data type (e.g., "INTEGER", "TEXT").
        not_null: Whether the column has a NOT NULL constraint.
        default_value: The default value for the column.
        primary_key: Whether the column is a primary key.
        cid: The column ID (used when parsing from PRAGMA table_info).
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
        """Initialize a SQLColumnInfoBase instance."""
        self._tables: set[SQLTableInfoBase] = set()
        self._table_names: set[str] = set()
        self.foreign_key = self._validate_foreign_key(foreign_key)
        self.check = check

        self.name = name
        self.data_type = data_type
        self.not_null = not_null or primary_key
        self.primary_key = primary_key
        self.unique = unique
        self.cid = cid
        self.default_value = autoconvert_default(default_value)

    def _validate_foreign_key(
        self, fk: dict[str, str] | None
    ) -> dict[str, str] | None:
        """Validate a foreign key definition.

        Args:
            fk: The foreign key dictionary to validate.

        Returns:
            The validated foreign key, or None if not provided.

        Raises:
            ValueError: If the foreign key is invalid.
        """
        if fk is None:
            return None
        if not isinstance(fk, dict) or "table" not in fk or "column" not in fk:
            raise ValueError(
                "Foreign key must be a dict with 'table' and 'column' keys"
            )
        if not all(isinstance(fk[k], str) for k in ("table", "column")):
            raise ValueError("Foreign key 'table' and 'column' must be strings")
        return fk

    def foreign_key_clause(self) -> str | None:
        """Generate the FOREIGN KEY clause for this column.

        Returns:
            The FOREIGN KEY clause string, or None if no foreign key.
        """
        if self.foreign_key:
            return (
                f"FOREIGN KEY ({ensure_quoted(self.name)}) "
                f"REFERENCES {self.foreign_key['table']}"
                f"({ensure_quoted(self.foreign_key['column'])})"
            )
        return None

    def _add_table(self, table: SQLTableInfoBase) -> None:
        """Add a table to the column's linked tables.

        Args:
            table: The table to link.

        Raises:
            TypeError: If table is not a SQLTableInfoBase instance.
        """
        if not isinstance(table, SQLTableInfoBase):
            raise TypeError("table must be an instance of SQLTableInfoBase")
        self._tables.add(table)
        self._table_names.add(table.name)
        table._column_dict[self.name] = self

    def _remove_table(self, table: SQLTableInfoBase) -> None:
        """Remove a table from the column's linked tables.

        Args:
            table: The table to unlink.

        Raises:
            TypeError: If table is not a SQLTableInfoBase instance.
        """
        if not isinstance(table, SQLTableInfoBase):
            raise TypeError("table must be an instance of SQLTableInfoBase")
        self._tables.discard(table)
        self._table_names.discard(table.name)
        table._column_dict.pop(self.name, None)

    @property
    def name(self) -> str:
        """Get the column name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the column name with validation.

        Args:
            value: The new column name.
        """
        validate_name(value)
        old_name = getattr(self, "_name", None)

        if old_name is not None and old_name != value:
            for table in self._tables:
                if old_name in table.column_dict:
                    table.column_dict[value] = table.column_dict.pop(old_name)
        self._name = value

    @property
    def data_type(self) -> str:
        """Get the column data type."""
        return self._data_type

    @data_type.setter
    def data_type(self, value: str) -> None:
        """Set the column data type with validation.

        Args:
            value: The new data type.

        Raises:
            ValueError: If the data type is invalid.
        """
        if not isinstance(value, str):
            raise ValueError(f"Invalid data type: {value}")
        if not validate_data_type(value):
            raise ValueError(f"Invalid SQL data type: {value}")
        self._data_type = upper_before_bracket(value.strip())

    @property
    def auto_increment(self) -> bool:
        """Check if the column is auto-increment.

        Returns:
            True if the column is a primary key with INTEGER type.
        """
        return self.primary_key and self.data_type.upper() in ["INTEGER", "INT"]

    @property
    def tables(self) -> set[SQLTableInfoBase]:
        """Get the set of tables this column is linked to."""
        return self._tables

    @tables.setter
    def tables(self, value: set[SQLTableInfoBase]) -> None:
        """Prevent direct setting of tables.

        Raises:
            TypeError: Always raised - use SQLTableInfoBase to set tables.
        """
        raise TypeError("tables must be set through the SQLTableInfoBase instance")

    @property
    def table_names(self) -> set[str]:
        """Get the set of table names this column is linked to."""
        return self._table_names

    @table_names.setter
    def table_names(self, value: set[str]) -> None:
        """Prevent direct setting of table names.

        Raises:
            TypeError: Always raised - use SQLTableInfoBase to set table names.
        """
        raise TypeError(
            "table_names must be set through the SQLTableInfoBase instance"
        )

    def to_dict(self) -> dict[str, str | int | float | bool | Unknown]:
        """Convert the column to a dictionary representation.

        Returns:
            Dictionary with column properties.
        """
        return {
            "cid": self.cid,
            "name": self.name,
            "data_type": self.data_type,
            "not_null": self.not_null,
            "default_value": get_value(self.default_value),
            "primary_key": self.primary_key,
            "unique": self.unique,
        }

    def to_raw_dict(self) -> dict[str, str | int | float | bool | None]:
        """Convert the column to a raw dictionary with None for unknown values.

        Returns:
            Dictionary with column properties, using None for unknown values.
        """
        base: dict[str, Any] = {
            "cid": None if is_undetermined(self.cid) else self.cid,
            "name": self.name,
            "data_type": self.data_type,
            "not_null": self.not_null,
            "default_value": (
                None
                if is_undetermined(get_value(self.default_value))
                else get_value(self.default_value)
            ),
            "primary_key": self.primary_key,
            "unique": self.unique,
        }
        if self.foreign_key:
            base["foreign_key"] = self.foreign_key
        return base

    def get_tuple(self) -> tuple[Any, ...]:
        """Convert the column to a tuple representation.

        Returns:
            Tuple with column properties.
        """
        return (
            self.cid,
            self.name,
            self.data_type,
            self.not_null,
            get_value(self.default_value),
            self.primary_key,
            self.auto_increment,
            self.unique,
        )

    def creation_str(self, supress_primary_key: bool = False) -> str:
        """Generate the SQL column definition string.

        Args:
            supress_primary_key: Whether to suppress PRIMARY KEY in output.

        Returns:
            SQL column definition string.
        """
        parts = [f"{ensure_quoted(self.name)} {self.data_type}"]

        if self.unique:
            parts.append("UNIQUE")
        if self.not_null and not self.primary_key:
            parts.append("NOT NULL")
        if self.primary_key and not supress_primary_key:
            parts.append("PRIMARY KEY")
        if self.auto_increment and not self.unique:
            parts.append("AUTOINCREMENT")
        if not is_undetermined(get_value(self.default_value)):
            default_str = format_default_value(self.default_value)
            parts.append(f"DEFAULT {default_str}")
        if self.check:
            parts.append(f"CHECK ({self.check.sql_string()})")

        return " ".join(parts)

    def validate(self) -> None:
        """Validate the column definition.

        Raises:
            ValueError: If the column definition is invalid.
        """
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Column name must be a non-empty string.")
        if not isinstance(self.data_type, str) or not validate_data_type(
            self.data_type
        ):
            raise ValueError(f"Invalid SQL data type: {self.data_type}")
        ensure_all_bools([self.not_null, self.primary_key, self.unique])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SQLColumnInfoBase:
        """Create a column from a dictionary.

        Args:
            data: Dictionary with column properties.

        Returns:
            A new SQLColumnInfoBase instance.
        """
        return cls(
            name=data["name"],
            data_type=data["data_type"],
            cid=data.get("cid", unknown),
            not_null=data.get("not_null", False),
            default_value=data.get("default_value", unknown),
            primary_key=data.get("primary_key", False),
            unique=data.get("unique", False),
        )

    @classmethod
    def from_tuple(cls, data: tuple[Any, ...]) -> SQLColumnInfoBase:
        """Create a column from a tuple.

        Args:
            data: Tuple with column properties.

        Returns:
            A new SQLColumnInfoBase instance.

        Raises:
            ValueError: If the tuple has fewer than 3 elements.
        """
        if len(data) < 3:
            raise ValueError(
                "Tuple must have at least 3 elements: (cid, name, data_type)"
            )
        cid, name, data_type = data[:3]
        not_null = bool(data[3]) if len(data) > 3 else False
        default = data[4] if len(data) > 4 else unknown
        primary_key = bool(data[5]) if len(data) > 5 else False
        unique = bool(data[7]) if len(data) > 7 else False

        return cls(
            cid=cid,
            name=name,
            data_type=data_type,
            not_null=not_null,
            default_value=default,
            primary_key=primary_key,
            unique=unique,
        )

    @staticmethod
    def can_be_column(
        data: dict[str, Any] | tuple[Any, ...] | SQLColumnInfoBase,
    ) -> bool:
        """Check if data can be converted to a column.

        Args:
            data: The data to check.

        Returns:
            True if the data can be converted to a column.
        """
        if isinstance(data, SQLColumnInfoBase):
            return True
        if isinstance(data, dict):
            return {"name", "data_type"}.issubset(data)
        if isinstance(data, tuple):
            return len(data) >= 3
        return False

    @staticmethod
    def return_column(
        data: dict[str, Any] | tuple[Any, ...] | SQLColumnInfoBase,
    ) -> SQLColumnInfoBase:
        """Convert data to a SQLColumnInfoBase instance.

        Args:
            data: The data to convert.

        Returns:
            A SQLColumnInfoBase instance.

        Raises:
            ValueError: If the data cannot be converted.
        """
        if isinstance(data, SQLColumnInfoBase):
            return data
        elif isinstance(data, dict):
            return SQLColumnInfoBase.from_dict(data)
        elif isinstance(data, tuple):
            return SQLColumnInfoBase.from_tuple(data)
        raise ValueError("Cannot convert to SQLColumnInfoBase")

    def __repr__(self) -> str:
        """Return a string representation of the column."""
        return (
            f"SQLColumnInfoBase(name={self.name}, data_type={self.data_type}, "
            f"not_null={self.not_null}, default_value={self.default_value}, "
            f"primary_key={self.primary_key})"
        )

    def __del__(self) -> None:
        """Clean up table references when column is deleted."""
        for table in self._tables:
            table._column_dict.pop(self.name, None)

    def __eq__(self, other: object) -> bool:
        """Check equality with another column.

        Args:
            other: The object to compare with.

        Returns:
            True if the columns are equal.
        """
        if not isinstance(other, SQLColumnInfoBase):
            return False
        return self.to_dict() == other.to_dict()

    def copy(self) -> SQLColumnInfoBase:
        """Create a copy of this column.

        Returns:
            A new SQLColumnInfoBase instance with the same properties.
        """
        return SQLColumnInfoBase(
            name=self.name,
            data_type=self.data_type,
            not_null=self.not_null,
            default_value=self.default_value,
            primary_key=self.primary_key,
            cid=self.cid,
            unique=self.unique,
            foreign_key=self.foreign_key,
            check=self.check,
        )


class SQLTableInfoBase(UndeterminedContainer):
    """Base class representing metadata for a SQL table.

    This class provides comprehensive support for table definitions including
    columns with various constraints and table-level foreign keys.

    Args:
        name: The table name.
        columns: Iterable of column definitions.
        database_path: Path to the database file.
        foreign_keys: List of table-level foreign key definitions.
    """

    def __init__(
        self,
        name: str,
        columns: Iterable[SQLColumnInfoBase] | Unknown = unknown,
        database_path: str | Unknown = unknown,
        foreign_keys: list[dict[str, list[str] | str]] | None = None,
    ) -> None:
        """Initialize a SQLTableInfoBase instance."""
        self.auto_increment_column: SQLColumnInfoBase | None = None
        self._columns: list[SQLColumnInfoBase] | Unknown = unknown
        self._column_dict: dict[str, SQLColumnInfoBase] = {}
        self._database_path: str | Unknown = unknown
        self.foreign_keys = foreign_keys or []

        self.name = name
        self.columns = columns
        self.database_path = database_path
        self.auto_increment_column = self._validate_auto_increment()

    @property
    def name(self) -> str:
        """Get the table name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the table name with validation.

        Args:
            value: The new table name.

        Raises:
            ValueError: If the name is invalid.
        """
        if not isinstance(value, str):
            raise ValueError(f"Invalid table name: {value}")
        validate_name(value)
        self._name = value

    @property
    def foreign_keys(self) -> list[dict[str, list[str] | str]]:
        """Get the list of table-level foreign keys."""
        return self._foreign_keys

    @foreign_keys.setter
    def foreign_keys(
        self, value: list[dict[str, list[str] | str]]
    ) -> None:
        """Set the foreign keys with validation.

        Args:
            value: List of foreign key definitions.

        Raises:
            ValueError: If any foreign key definition is invalid.
        """
        for i, fk in enumerate(value):
            if not isinstance(fk, dict):
                raise ValueError(f"Foreign key at index {i} must be a dict")
            if not all(k in fk for k in ("columns", "ref_table", "ref_columns")):
                raise ValueError(
                    f"Foreign key at index {i} must have keys: "
                    "columns, ref_table, ref_columns"
                )
            if not isinstance(fk["columns"], list) or not isinstance(
                fk["ref_columns"], list
            ):
                raise ValueError(
                    f"Foreign key at index {i} columns and ref_columns must be lists"
                )
            if len(fk["columns"]) != len(fk["ref_columns"]):
                raise ValueError(
                    f"Foreign key at index {i} columns and ref_columns "
                    "must be the same length"
                )

            # Strip whitespace from all string values
            fk["columns"] = [c.strip() for c in fk["columns"]]
            fk["ref_columns"] = [ref_col.strip() for ref_col in fk["ref_columns"]]
            fk["ref_table"] = fk["ref_table"].strip()
            value[i] = fk

        self._foreign_keys = value

    @property
    def database_path(self) -> str | Unknown:
        """Get the database path."""
        return self._database_path

    @database_path.setter
    def database_path(self, value: str | Unknown) -> None:
        """Set the database path with validation.

        Args:
            value: The database path or unknown.
        """
        if not is_undetermined(value):
            validate_database_path(value)
        self._database_path = value

    @property
    def column_dict(self) -> dict[str, SQLColumnInfoBase]:
        """Get the dictionary mapping column names to columns."""
        return self._column_dict

    @column_dict.setter
    def column_dict(self, value: dict[str, SQLColumnInfoBase]) -> None:
        """Prevent direct setting of column_dict.

        Raises:
            TypeError: Always raised - use columns property instead.
        """
        raise TypeError("column_dict must be set through columns property")

    @property
    def columns(self) -> list[SQLColumnInfoBase]:
        """Get the list of columns."""
        return [] if is_undetermined(self._columns) else self._columns

    @columns.setter
    def columns(self, value: Iterable[SQLColumnInfoBase] | Unknown) -> None:
        """Set the columns with validation.

        Args:
            value: Iterable of column definitions.

        Raises:
            TypeError: If value is not a valid iterable.
        """
        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            raise TypeError(
                "Columns must be an iterable of SQLColumnInfoBase objects"
            )

        new_columns = self.validate_columns(value)
        self._update_columns(new_columns)

    def add_column(self, column: SQLColumnInfoBase) -> None:
        """Add a new column to the table.

        Args:
            column: The column to add.

        Raises:
            ValueError: If a column with the same name already exists.
        """
        self.validate_new_column(column)
        column._add_table(self)
        self._columns.append(column)
        if column.auto_increment:
            self.auto_increment_column = self._validate_auto_increment()

    def remove_column(self, column_name: str) -> None:
        """Remove a column from the table by name.

        Args:
            column_name: The name of the column to remove.

        Raises:
            TypeError: If column_name is not a string.
            ValueError: If the column does not exist.
        """
        if not isinstance(column_name, str):
            raise TypeError("Column name must be a string")
        if column_name not in self._column_dict:
            raise ValueError(
                f"Column '{column_name}' does not exist in table '{self.name}'"
            )

        column = self._column_dict.get(column_name)
        column._remove_table(self)
        self._columns.remove(column)

        if column.auto_increment and self.auto_increment_column == column:
            self.auto_increment_column = self._validate_auto_increment()

    def validate_new_column(self, column: SQLColumnInfoBase) -> None:
        """Validate that a new column can be added.

        Args:
            column: The column to validate.

        Raises:
            TypeError: If column is not a SQLColumnInfoBase instance.
            ValueError: If the column name already exists or auto-increment conflict.
        """
        if not isinstance(column, SQLColumnInfoBase):
            raise TypeError("New column must be an instance of SQLColumnInfoBase")
        if column.name in self._column_dict:
            raise ValueError(
                f"Column with name '{column.name}' already exists in "
                f"table '{self.name}'"
            )
        if column.auto_increment and self.auto_increment_column is not None:
            raise ValueError("Only one column can be auto increment in a table")

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
                column._remove_table(self)

        # Add new ones
        for column in new_columns:
            self.validate_new_column(column)
            column._add_table(self)

        self._columns = new_columns

    def _validate_auto_increment(self) -> SQLColumnInfoBase | None:
        """Validate and return the auto-increment column if present.

        Returns:
            The auto-increment column, or None if none exists.

        Raises:
            ValueError: If multiple auto-increment columns or invalid config.
        """
        primary_keys = self.get_primary_keys()
        if len(primary_keys) == 1:
            auto_columns = [col for col in primary_keys if col.auto_increment]
        else:
            auto_columns = []

        if len(auto_columns) > 1:
            raise ValueError("Only one column can be auto increment")
        if auto_columns and not auto_columns[0].primary_key:
            raise ValueError("Auto increment column must be a primary key")
        return auto_columns[0] if auto_columns else None

    def sql_creation_str(self, if_not_exists: bool = False) -> str:
        """Generate the SQL CREATE TABLE statement.

        Args:
            if_not_exists: Whether to include IF NOT EXISTS clause.

        Returns:
            The SQL CREATE TABLE statement.
        """
        if_not_exists_clause = " IF NOT EXISTS" if if_not_exists else ""
        primary_keys = self.get_primary_keys()
        use_composite_pk = len(primary_keys) > 1

        column_defs = [
            col.creation_str(supress_primary_key=use_composite_pk)
            for col in self.columns
        ]

        if use_composite_pk:
            pk_names = ', '.join(ensure_quoted(col.name) for col in primary_keys)
            pk_clause = f"PRIMARY KEY ({pk_names})"
            column_defs.append(pk_clause)

        extra_column_defs: set[str] = set()

        # Single-column FKs from columns
        for column in self.columns:
            fk_clause = column.foreign_key_clause()
            if fk_clause:
                extra_column_defs.add(fk_clause)

        # Composite foreign keys
        for fk in self.foreign_keys:
            col_names = ", ".join(ensure_quoted(c) for c in fk["columns"])
            ref_table = fk["ref_table"]
            ref_cols = ", ".join(ensure_quoted(c) for c in fk["ref_columns"])
            constraint = (
                f"FOREIGN KEY ({col_names}) "
                f"REFERENCES {ref_table}({ref_cols})"
            )
            if "on_delete" in fk:
                constraint += f" ON DELETE {fk['on_delete'].upper()}"
            if "on_update" in fk:
                constraint += f" ON UPDATE {fk['on_update'].upper()}"
            extra_column_defs.add(constraint)

        column_defs.extend(extra_column_defs)

        return (
            f"CREATE TABLE{if_not_exists_clause} "
            f"{ensure_quoted(self.name)} ({', '.join(column_defs)});"
        )

    def creation_str(self, if_not_exists: bool = False) -> str:
        """Generate the SQL CREATE TABLE statement.

        Alias for sql_creation_str.

        Args:
            if_not_exists: Whether to include IF NOT EXISTS clause.

        Returns:
            The SQL CREATE TABLE statement.
        """
        return self.sql_creation_str(if_not_exists)

    def to_dict(self) -> dict[str, str | list[SQLColumnInfoBase] | Unknown]:
        """Convert the table to a dictionary representation.

        Returns:
            Dictionary with table properties.
        """
        return {
            "name": self.name,
            "columns": self.columns,
            "database_path": self.database_path,
        }

    def to_raw_dict(self) -> dict[str, str | list[dict[str, Any]] | None]:
        """Convert the table to a raw dictionary with None for unknown values.

        Returns:
            Dictionary with table properties, using None for unknown values.
        """
        return {
            "name": self.name,
            "columns": (
                [col.to_raw_dict() for col in self.columns]
                if not is_undetermined(self.columns)
                else []
            ),
            "database_path": (
                None if is_undetermined(self.database_path) else self.database_path
            ),
        }

    def get_primary_keys(self) -> list[SQLColumnInfoBase]:
        """Get the list of primary key columns.

        Returns:
            List of columns that are primary keys.
        """
        return [col for col in self.columns if col.primary_key]

    def __eq__(self, other: object) -> bool:
        """Check equality with another table.

        Args:
            other: The object to compare with.

        Returns:
            True if the tables are equal.
        """
        if not isinstance(other, SQLTableInfoBase):
            return False
        return self.name == other.name and self.database_path == other.database_path

    def __hash__(self) -> int:
        """Return a hash value for the table.

        Returns:
            Hash value based on name and database_path.
        """
        return hash(self.name) ^ hash(self.database_path)

    @classmethod
    def from_data(
        cls,
        table_name: str,
        row: dict[str, Any],
        primary_keys: list[str] | None = None,
        datatypes: dict[str, str] | None = None,
        default_values: dict[str, Any] | None = None,
        not_null_values: dict[str, bool] | None = None,
        unique_cols: list[str] | None = None,
        auto_primary_key: bool = True,
    ) -> SQLTableInfoBase:
        """Create a table from a data row.

        Args:
            table_name: The table name.
            row: Dictionary representing a data row.
            primary_keys: List of primary key column names.
            datatypes: Dictionary mapping column names to data types.
            default_values: Dictionary mapping column names to default values.
            not_null_values: Dictionary mapping column names to NOT NULL flags.
            unique_cols: List of unique column names.
            auto_primary_key: Whether to auto-assign primary key to first column.

        Returns:
            A new SQLTableInfoBase instance.

        Raises:
            ValueError: If row is not a dictionary.
        """
        if not isinstance(row, dict):
            raise ValueError("Row must be a dictionary")
        if not row:
            return cls(name=table_name, columns=[], database_path=unknown)

        primary_keys = primary_keys or []
        datatypes = datatypes or {}
        default_values = default_values or {}
        not_null_values = not_null_values or {}
        unique_cols = unique_cols or []

        type_map = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bool: "BOOLEAN",
            bytes: "BLOB",
        }

        columns: list[SQLColumnInfoBase] = []
        assigned_primary = False

        for i, (col_name, value) in enumerate(row.items()):
            dtype = datatypes.get(col_name)
            if not dtype or not validate_data_type(dtype):
                dtype = type_map.get(type(value), "TEXT")

            is_pk = col_name in primary_keys
            if (
                not assigned_primary
                and auto_primary_key
                and not primary_keys
                and i == 0
            ):
                is_pk = True
                assigned_primary = True

            column = SQLColumnInfoBase(
                name=col_name,
                data_type=dtype,
                not_null=not_null_values.get(col_name, False) or is_pk,
                default_value=default_values.get(col_name, unknown),
                primary_key=is_pk,
                unique=col_name in unique_cols,
            )
            columns.append(column)

        return cls(name=table_name, columns=columns, database_path=unknown)

    def __repr__(self) -> str:
        """Return a string representation of the table."""
        return (
            f"SQLTableInfoBase(name={self.name}, "
            f"columns=({', '.join(col.name for col in self.columns)}), "
            f"database_path={self.database_path})"
        )

    def __del__(self) -> None:
        """Clean up column references when table is deleted."""
        for column in self.columns:
            column._tables.discard(self)
            column._table_names.discard(self.name)

    def copy(self) -> SQLTableInfoBase:
        """Create a copy of this table.

        Returns:
            A new SQLTableInfoBase instance with the same properties.
        """
        return SQLTableInfoBase(
            name=self.name,
            columns=[col.copy() for col in self.columns],
            database_path=self.database_path,
            foreign_keys=self.foreign_keys,
        )

    def copy_without_cols(self, *column_names: str) -> SQLTableInfoBase:
        """Create a copy of this table without specified columns.

        Args:
            *column_names: Names of columns to exclude.

        Returns:
            A new SQLTableInfoBase instance without the specified columns.
        """
        new_columns = [
            col.copy() for col in self.columns if col.name not in column_names
        ]
        return SQLTableInfoBase(
            name=self.name,
            columns=new_columns,
            database_path=self.database_path,
            foreign_keys=self.foreign_keys,
        )

    @staticmethod
    def validate_columns(
        columns: Iterable[SQLColumnInfoBase] | Unknown,
    ) -> list[SQLColumnInfoBase]:
        """Validate and convert columns to a list.

        Args:
            columns: Iterable of column definitions.

        Returns:
            List of validated columns.
        """
        if SQLColumnInfoBase.can_be_column(columns):
            columns = SQLColumnInfoBase.return_column(columns)
        if isinstance(columns, SQLColumnInfoBase):
            columns = [columns]
        elif isinstance(columns, Iterable) and not isinstance(columns, str):
            columns = [SQLColumnInfoBase.return_column(column) for column in columns]
        return columns


def main(writer = None):
    """Demo function to create and display sample SQL table definitions."""
    if writer is None:
        register = print
    else:
        register = writer.write_words_line
    # Define the Owners table
    owner_columns = [
        SQLColumnInfoBase("id", "INTEGER", primary_key=True),
        SQLColumnInfoBase("name", "TEXT", not_null=True),
        SQLColumnInfoBase("email", "TEXT", unique=True, not_null=True)
    ]

    owners_table = SQLTableInfoBase(
        name="owners",
        columns=owner_columns
    )

    # Define the Pets table with a foreign key to owners.id
    pet_columns = [
        SQLColumnInfoBase("id", "INTEGER", primary_key=True),
        SQLColumnInfoBase("name", "TEXT", not_null=True),
        SQLColumnInfoBase("species", "TEXT", default_value="Unknown"),
        SQLColumnInfoBase("age", "INTEGER", default_value=0),
        SQLColumnInfoBase("vaccinated", "BOOLEAN", default_value=False),
        SQLColumnInfoBase(
            "owner_id", "INTEGER", not_null=True,
            foreign_key={"table": "owners", "column": "id"}
        )
    ]

    pets_table = SQLTableInfoBase(
        name="pets",
        columns=pet_columns
    )

    # Show SQL CREATE statements
    register(owners_table.creation_str(if_not_exists=True))
    register(pets_table.creation_str(if_not_exists=True))
