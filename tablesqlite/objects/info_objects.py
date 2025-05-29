from __future__ import annotations
from typing import Union, Iterable, Dict, List, Set, Optional
from expressQL import SQLCondition, SQLExpression, col
from ..validation import validate_data_type, validate_name, ensure_all_bools
from .generic import Unknown, unknown, is_undetermined, ensure_quoted
from ..validation import (validate_database_path, ensure_all_bools, upper_before_bracket,
    add_bool_properties, add_undetermined_properties,
    DualContainer, UndeterminedContainer)

SQL_LITERAL_DEFAULTS = {
    "CURRENT_TIME",
    "CURRENT_DATE",
    "CURRENT_TIMESTAMP",
    "NULL"  # possibly, though quoting it wouldn't break things
}

def autoconvert_default(value):
    if isinstance(value, str) and value.upper() in SQL_LITERAL_DEFAULTS:
        return col(value.upper())
    return value

def get_value(item:str | int | float | SQLExpression) -> Union[str, int, float, SQLExpression]:
    """
    Returns the value of the item if it is not an instance of Unknown.
    """
    if isinstance(item, Unknown):
        return unknown
    elif isinstance(item, SQLExpression):
        return item.true_value()
    
    return item

def format_default_value(val) -> str:
    if isinstance(val, SQLExpression):
        return val.sql_string()
    elif isinstance(val, str):
        return f"'{val}'"
    else:
        return str(val)


@add_bool_properties('not_null', 'primary_key', 'unique')
@add_undetermined_properties(cid=int, default_value=Union[str, int, float, SQLExpression])
class SQLColumnInfoBase(DualContainer):
    def __init__(
        self,
        name: str,
        data_type: str,
        not_null: bool = False,
        default_value: Union[str, int, float, Unknown] = unknown,
        primary_key: bool = False,
        cid: Union[int, Unknown] = unknown,
        *,
        unique: bool = False,
        foreign_key: Union[None, Dict[str, str]] = None,
        check: Optional[SQLCondition] = None  # New field for CHECK
    ):
        
        self._tables: Set['SQLTableInfoBase'] = set()
        self._table_names: Set[str] = set()
        self.foreign_key = self._validate_foreign_key(foreign_key)
        self.check = check

        self.name = name
        self.data_type = data_type
        self.not_null = not_null or primary_key
        self.primary_key = primary_key
        self.unique = unique
        self.cid = cid
        self.default_value = autoconvert_default(default_value)

    def _validate_foreign_key(self, fk: Union[None, Dict[str, str]]) -> Union[None, Dict[str, str]]:
        if fk is None:
            return None
        if not isinstance(fk, dict) or 'table' not in fk or 'column' not in fk:
            raise ValueError("Foreign key must be a dict with 'table' and 'column' keys")
        if not all(isinstance(fk[k], str) for k in ('table', 'column')):
            raise ValueError("Foreign key 'table' and 'column' must be strings")
        return fk


    def foreign_key_clause(self) -> Union[str, None]:
        if self.foreign_key:
            return f"FOREIGN KEY ({ensure_quoted(self.name)}) REFERENCES {self.foreign_key['table']}({ensure_quoted(self.foreign_key['column'])})"
        return None

    def _add_table(self, table: 'SQLTableInfoBase'):
        """
        Adds a table to the column's linked tables.
        """
        if not isinstance(table, SQLTableInfoBase):
            raise TypeError("table must be an instance of SQLTableInfoBase")
        self._tables.add(table)
        self._table_names.add(table.name)
        table._column_dict[self.name] = self
    def _remove_table(self, table: 'SQLTableInfoBase'):
        """
        Removes a table from the column's linked tables.
        """
        if not isinstance(table, SQLTableInfoBase):
            raise TypeError("table must be an instance of SQLTableInfoBase")
        self._tables.discard(table)
        self._table_names.discard(table.name)
        table._column_dict.pop(self.name, None)
    # --- Properties ---

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        validate_name(value)
        old_name = getattr(self, '_name', None)

        if old_name is not None and old_name != value:
            for table in self._tables:
                if old_name in table.column_dict:
                    table.column_dict[value] = table.column_dict.pop(old_name)
        self._name = value

    @property
    def data_type(self) -> str:
        return self._data_type

    @data_type.setter
    def data_type(self, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Invalid data type: {value}")
        if not validate_data_type(value):
            raise ValueError(f"Invalid SQL data type: {value}")
        self._data_type = upper_before_bracket(value.strip())

    @property
    def auto_increment(self) -> bool:
        return self.primary_key and self.data_type.upper() in ["INTEGER", "INT"]


    @property
    def tables(self) -> Set['SQLTableInfoBase']:
        return self._tables
    @tables.setter
    def tables(self, value: Set['SQLTableInfoBase']):
        raise TypeError("tables must be set through the SQLTableInfoBase instance")
    @property
    def table_names(self) -> Set[str]:
        return self._table_names
    @table_names.setter
    def table_names(self, value: Set[str]):
        raise TypeError("table_names must be set through the SQLTableInfoBase instance")

    # --- Conversions ---

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, Unknown]]:
        return {
            "cid": self.cid,
            "name": self.name,
            "data_type": self.data_type,
            "not_null": self.not_null,
            "default_value": get_value(self.default_value),
            "primary_key": self.primary_key,
            "unique": self.unique,
        }

    def to_raw_dict(self) -> Dict[str, Union[str, int, float, bool, None]]:
        base = {
            "cid": None if is_undetermined(self.cid) else self.cid,
            "name": self.name,
            "data_type": self.data_type,
            "not_null": self.not_null,
            "default_value": None if is_undetermined(get_value(self.default_value)) else get_value(self.default_value),
            "primary_key": self.primary_key,
            "unique": self.unique,
        }
        if self.foreign_key:
            base["foreign_key"] = self.foreign_key
        return base


    def get_tuple(self) -> tuple:
        return (
            self.cid,
            self.name,
            self.data_type,
            self.not_null,
            get_value(self.default_value),
            self.primary_key,
            self.auto_increment,
            self.unique
        )

    # --- Creation SQL ---

    def creation_str(self, supress_primary_key: bool = False) -> str:
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

    # --- Validation Utility ---

    def validate(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Column name must be a non-empty string.")
        if not isinstance(self.data_type, str) or not validate_data_type(self.data_type):
            raise ValueError(f"Invalid SQL data type: {self.data_type}")
        ensure_all_bools([self.not_null, self.primary_key, self.unique])

    # --- Static Builders ---

    @classmethod
    def from_dict(cls, data: Dict) -> 'SQLColumnInfoBase':
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
    def from_tuple(cls, data: tuple) -> 'SQLColumnInfoBase':
        if len(data) < 3:
            raise ValueError("Tuple must have at least 3 elements: (cid, name, data_type)")
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
            unique=unique
        )

    @staticmethod
    def can_be_column(data: Union[Dict, tuple, 'SQLColumnInfoBase']) -> bool:
        if isinstance(data, SQLColumnInfoBase):
            return True
        if isinstance(data, dict):
            return {"name", "data_type"}.issubset(data)
        if isinstance(data, tuple):
            return len(data) >= 3
        return False

    @staticmethod
    def return_column(data: Union[Dict, tuple, 'SQLColumnInfoBase']) -> 'SQLColumnInfoBase':
        if isinstance(data, SQLColumnInfoBase):
            return data
        elif isinstance(data, dict):
            return SQLColumnInfoBase.from_dict(data)
        elif isinstance(data, tuple):
            return SQLColumnInfoBase.from_tuple(data)
        raise ValueError("Cannot convert to SQLColumnInfoBase")

    # --- Representation ---

    def __repr__(self):
        return (
            f"SQLColumnInfoBase(name={self.name}, data_type={self.data_type}, "
            f"not_null={self.not_null}, default_value={self.default_value}, "
            f"primary_key={self.primary_key})"
        )
    
    def __del__(self):
        for table in self._tables:
            table._column_dict.pop(self.name, None)

    def __eq__(self, other):
        if not isinstance(other, SQLColumnInfoBase):
            return False
        return self.to_dict() == other.to_dict()

    def copy(self) -> SQLColumnInfoBase:
        """
        Returns a copy of the SQLColumnInfoBase instance.
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
            check=self.check
        )

class SQLTableInfoBase(UndeterminedContainer):
    """
    Represents metadata for a SQL table.
    """
    def __init__(
        self,
        name: str,
        columns: Union[Iterable[SQLColumnInfoBase], Unknown] = unknown,
        database_path: Union[str, Unknown] = unknown,
        foreign_keys: List[Dict[str, Union[List[str], str, Dict[str, str]]]] = None
    ):
        self.auto_increment_column = None
        self._columns: Union[List[SQLColumnInfoBase], Unknown] = unknown
        self._column_dict: Dict[str, SQLColumnInfoBase] = {}
        self._database_path = unknown
        self.foreign_keys = foreign_keys or []

        self.name = name
        self.columns = columns
        self.database_path = database_path
        self.auto_increment_column = self._validate_auto_increment()


    # --- Properties ---

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Invalid table name: {value}")
        validate_name(value)
        self._name = value

    @property
    def foreign_keys(self) -> List[Dict[str, Union[List[str], str]]]:
        return self._foreign_keys

    @foreign_keys.setter
    def foreign_keys(self, value: List[Dict[str, Union[List[str], str]]]):
        for i, fk in enumerate(value):
            if not isinstance(fk, dict):
                raise ValueError(f"Foreign key at index {i} must be a dict")
            if not all(k in fk for k in ("columns", "ref_table", "ref_columns")):
                raise ValueError(f"Foreign key at index {i} must have keys: columns, ref_table, ref_columns")
            if not isinstance(fk["columns"], list) or not isinstance(fk["ref_columns"], list):
                raise ValueError(f"Foreign key at index {i} columns and ref_columns must be lists")
            if len(fk["columns"]) != len(fk["ref_columns"]):
                raise ValueError(f"Foreign key at index {i} columns and ref_columns must be the same length")

            # Strip whitespace from all string values in the foreign key dict
            fk["columns"] = [col.strip() for col in fk["columns"]]
            fk["ref_columns"] = [ref_col.strip() for ref_col in fk["ref_columns"]]
            fk["ref_table"] = fk["ref_table"].strip()
            value[i] = fk

            
        self._foreign_keys = value


    @property
    def database_path(self) -> Union[str, Unknown]:
        return self._database_path

    @database_path.setter
    def database_path(self, value: Union[str, Unknown]):
        if not is_undetermined(value):
            validate_database_path(value)
        self._database_path = value

    @property
    def column_dict(self) -> Dict[str, SQLColumnInfoBase]:
        return self._column_dict

    @column_dict.setter
    def column_dict(self, value):
        raise TypeError("column_dict must be set through columns property")

    @property
    def columns(self) -> List[SQLColumnInfoBase]:
        return [] if is_undetermined(self._columns) else self._columns

    @columns.setter
    def columns(self, value: Union[Iterable[SQLColumnInfoBase], Unknown]):
        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            raise TypeError("Columns must be an iterable of SQLColumnInfoBase objects")

        new_columns = self.validate_columns(value)
        self._update_columns(new_columns)
    def add_column(self, column: SQLColumnInfoBase) -> None:
        """
        Adds a new column to the table without triggering a full update.
        """
        self.validate_new_column(column)
        column._add_table(self)
        self._columns.append(column)
        if column.auto_increment:
            self.auto_increment_column = self._validate_auto_increment()
    def remove_column(self, column_name: str) -> None:
        """
        Removes a column from the table by name without triggering a full update.
        """
        if not isinstance(column_name, str):
            raise TypeError("Column name must be a string")
        if column_name not in self._column_dict:
            raise ValueError(f"Column '{column_name}' does not exist in table '{self.name}'")
        
        column = self._column_dict.get(column_name)
        column._remove_table(self)
        self._columns.remove(column)
        
        if column.auto_increment and self.auto_increment_column == column:
            self.auto_increment_column = self._validate_auto_increment()
    # --- Internal Helpers ---
    def validate_new_column(self, column: SQLColumnInfoBase) -> None:
        if not isinstance(column, SQLColumnInfoBase):
            raise TypeError("New column must be an instance of SQLColumnInfoBase")
        if column.name in self._column_dict:
            raise ValueError(f"Column with name '{column.name}' already exists in table '{self.name}'")
        if column.auto_increment and self.auto_increment_column is not None:
            raise ValueError("Only one column can be auto increment in a table")
    def _update_columns(self, new_columns: List[SQLColumnInfoBase]):
        """
        Update internal state with new column list.
        Handles _tables linkage and dictionary sync.
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

    def _validate_auto_increment(self) -> Union[SQLColumnInfoBase, None]:
        auto_columns = [col for col in self.columns if col.auto_increment]
        if len(auto_columns) > 1:
            raise ValueError("Only one column can be auto increment")
        if auto_columns and not auto_columns[0].primary_key:
            raise ValueError("Auto increment column must be a primary key")
        return auto_columns[0] if auto_columns else None

    # --- SQL Methods ---

    def sql_creation_str(self, if_not_exists: bool = False) -> str:
        if_not_exists_clause = " IF NOT EXISTS" if if_not_exists else ""
        primary_keys = self.get_primary_keys()
        use_composite_pk = len(primary_keys) > 1

        column_defs = [
            col.creation_str(supress_primary_key=use_composite_pk)
            for col in self.columns
        ]

        # Composite PK support
        if use_composite_pk:
            pk_clause = f"PRIMARY KEY ({', '.join(ensure_quoted(col.name) for col in primary_keys)})"
            column_defs.append(pk_clause)
        extra_column_defs = set()
        # Single-column FKs from columns
        for col in self.columns:
            fk_clause = col.foreign_key_clause()
            if fk_clause:
                extra_column_defs.add(fk_clause)
                #column_defs.append(fk_clause)

        # Composite foreign keys (re-enable this!)
        for fk in self.foreign_keys:
            col_names = ", ".join(ensure_quoted(c) for c in fk["columns"])
            ref_table = fk["ref_table"]
            ref_cols  = ", ".join(ensure_quoted(c) for c in fk["ref_columns"])
            constraint = (
                f"FOREIGN KEY ({col_names}) "
                f"REFERENCES {ref_table}({ref_cols})"
            )
            if "on_delete" in fk:
                constraint += f" ON DELETE {fk['on_delete'].upper()}"
            if "on_update" in fk:
                constraint += f" ON UPDATE {fk['on_update'].upper()}"
            extra_column_defs.add(constraint)
            #column_defs.append(constraint)
        column_defs.extend(extra_column_defs)



        return f"CREATE TABLE{if_not_exists_clause} {ensure_quoted(self.name)} ({', '.join(column_defs)});"

    def creation_str(self, if_not_exists: bool = False) -> str:
        return self.sql_creation_str(if_not_exists)

    # --- Conversion Methods ---

    def to_dict(self) -> Dict[str, Union[str, List[SQLColumnInfoBase], Unknown]]:
        return {
            "name": self.name,
            "columns": self.columns,
            "database_path": self.database_path,
        }

    def to_raw_dict(self) -> Dict[str, Union[str, List[Dict], None]]:
        return {
            "name": self.name,
            "columns": [
                col.to_raw_dict() for col in self.columns
            ] if not is_undetermined(self.columns) else [],
            "database_path": None if is_undetermined(self.database_path) else self.database_path,
        }

    # --- Primary Key Logic ---

    def get_primary_keys(self) -> List[SQLColumnInfoBase]:
        return [col for col in self.columns if col.primary_key]

    # --- Equality & Hashing ---

    def __eq__(self, other):
        if not isinstance(other, SQLTableInfoBase):
            return False
        return self.name == other.name and self.database_path == other.database_path

    def __hash__(self):
        return hash(self.name) ^ hash(self.database_path)

    # --- Creation from Data ---

    @classmethod
    def from_data(
        cls,
        table_name: str,
        row: Dict,
        primary_keys: List[str] = None,
        datatypes: Dict[str, str] = None,
        default_values: Dict = None,
        not_null_values: Dict = None,
        unique_cols: List[str] = None,
        auto_primary_key: bool = True
    ) -> SQLTableInfoBase:
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
            bytes: "BLOB"
        }

        columns = []
        assigned_primary = False

        for i, (col_name, value) in enumerate(row.items()):
            dtype = datatypes.get(col_name)
            if not dtype or not validate_data_type(dtype):
                dtype = type_map.get(type(value), "TEXT")

            is_pk = col_name in primary_keys
            if not assigned_primary and auto_primary_key and not primary_keys and i == 0:
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

    # --- Debug Representation ---

    def __repr__(self):
        return (
            f"SQLTableInfoBase(name={self.name}, "
            f"columns=({', '.join(col.name for col in self.columns)}), "
            f"database_path={self.database_path})"
        )
    
    def __del__(self):
        for column in self.columns:
            column._tables.discard(self)
            column._table_names.discard(self.name)

    def copy(self) -> SQLTableInfoBase:
        """
        Returns a copy of the SQLTableInfoBase instance.
        """
        return SQLTableInfoBase(
            name=self.name,
            columns=[col.copy() for col in self.columns],
            database_path=self.database_path,
            foreign_keys=self.foreign_keys
        )
    def copy_without_cols(self, *column_names: str) -> SQLTableInfoBase:
        """
        Returns a copy of the SQLTableInfoBase instance without specified columns.
        """
        new_columns = [col.copy() for col in self.columns if col.name not in column_names]
        return SQLTableInfoBase(
            name=self.name,
            columns=new_columns,
            database_path=self.database_path,
            foreign_keys=self.foreign_keys
        )
    @staticmethod
    def validate_columns(columns:List[SQLColumnInfoBase]) -> List[SQLColumnInfoBase]:
        if SQLColumnInfoBase.can_be_column(columns):
            columns = SQLColumnInfoBase.return_column(columns)
        if isinstance(columns, SQLColumnInfoBase):
            columns = [columns]
        elif isinstance(columns, Iterable) and not isinstance(columns, str):
            columns = [SQLColumnInfoBase.return_column(column) for column in columns]
        return columns

def main(writer = None):
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
