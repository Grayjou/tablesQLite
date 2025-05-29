from typing import Union, Iterable, List, Dict, Optional, Tuple, Any
from .objects import SQLTableInfoBase, SQLColumnInfoBase, unknown, Unknown, is_undetermined
from expressQL import SQLCondition
from .action_queries import (
    add_column_query,
    drop_column_query,
    rename_column_query,
    create_table_query,
    drop_table_query,
    rename_table_query,
)
from .info_queries import (
    parse_sql_schema)



class SQLColumnInfo(SQLColumnInfoBase):
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
        check: Optional[SQLCondition] = None
    ):
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
        table_name: Optional[str],
        check_in_tables: bool = False,
        solve_by: str = "raise"
    ) -> Optional[str]:
        if table_name is not None:
            if check_in_tables and table_name not in self.table_names:
                match solve_by.lower():
                    case "raise":
                        raise ValueError(f"Table '{table_name}' not found in column's linked tables.")
                    case "ignore":
                        return table_name
                    case "none":
                        return None
                    case _:
                        raise ValueError(f"Invalid solve_by value: {solve_by}")
            return table_name

        table_count = len(self._tables)
        if table_count == 1:
            return next(iter(self._tables)).name
        elif table_count > 1:
            raise ValueError("Column is linked to multiple tables. Specify 'table_name'.")
        else:
            raise ValueError("Column is not linked to any table. Specify 'table_name'.")

    def drop_query(
        self,
        table_name: Optional[str] = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise"
    ) -> tuple[str, List]:
        table_name = self._resolve_table_name(table_name, check_in_tables, solve_by)
        return drop_column_query(table_name, self.name, check_if_possible=check_if_possible)

    def rename_query(
        self,
        new_name: str,
        table_name: Optional[str] = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise"
    ) -> tuple[str, List]:
        table_name = self._resolve_table_name(table_name, check_in_tables, solve_by)
        return rename_column_query(table_name, self.name, new_name, check_if_possible=check_if_possible)

    def add_query(
        self,
        table_name: Optional[str] = None,
        check_if_possible: bool = False,
        check_in_tables: bool = False,
        *,
        solve_by: str = "raise"
    ) -> tuple[str, List]:
        table_name = self._resolve_table_name(table_name, check_in_tables, solve_by)
        return add_column_query(table_name, self, check_if_possible=check_if_possible)

    @classmethod
    def from_super(cls, column: SQLColumnInfoBase) -> 'SQLColumnInfo':
        return cls(
            name=column.name,
            data_type=column.data_type,
            not_null=column.not_null,
            default_value=column.default_value,
            primary_key=column.primary_key,
            cid=column.cid,
            unique=column.unique,
            foreign_key=column.foreign_key,
            check=column.check
        )

    @classmethod
    def ensure_subclass(cls, column: SQLColumnInfoBase) -> 'SQLColumnInfo':
        if isinstance(column, cls):
            return column
        return cls.from_super(column)

class SQLTableInfo(SQLTableInfoBase):
    def __init__(
        self,
        name: str,
        columns: Union[Iterable[SQLColumnInfo], Unknown] = unknown,
        database_path: Union[str, Unknown] = unknown,
        foreign_keys: List[Dict[str, Union[List[str], str, Dict[str, str]]]] = None
    ):
        super().__init__(name, columns, database_path, foreign_keys)

    def drop_query(self, if_exists: bool = False) -> tuple[str, List]:
        return drop_table_query(self, check_if_exists=if_exists)
    def rename_query(self, new_name: str, if_exists: bool = False) -> tuple[str, List]:
        return rename_table_query(self.name, new_name, check_if_exists=if_exists)
    def create_query(self) -> tuple[str, List]:
        return create_table_query(self)
    def add_column_query(self, column: SQLColumnInfoBase, check_if_possible: bool = False) -> tuple[str, List]:
        return add_column_query(self, column, check_if_possible=check_if_possible)
    def drop_column_query(self, column_name: str, check_if_possible: bool = False) -> tuple[str, List]:
        return drop_column_query(self, column_name, check_if_possible=check_if_possible)
    def rename_column_query(self, old_name: str, new_name: str, check_if_possible: bool = False) -> tuple[str, List]:
        return rename_column_query(self, old_name, new_name, check_if_possible=check_if_possible)
    @classmethod
    def from_super(cls, table: SQLTableInfoBase) -> 'SQLTableInfo':
        """
        Create a SQLTableInfo instance from a SQLTableInfoBase instance.
        """

        return cls(
            name=table.name,
            columns=table.columns,
            database_path=table.database_path,
            foreign_keys=table.foreign_keys
        )
    @classmethod
    def from_sql_schema(cls, schema: Union[str, List[Dict]]) -> 'SQLTableInfo':
        """
        Create a SQLTableInfoBase instance from a SQL schema string or a list of dictionaries.
        """
        return cls.from_super(parse_sql_schema(schema))

    def add_column(self, column: SQLColumnInfoBase) -> None:
        """
        Adds a new column to the table without triggering a full update.
        """
        column = SQLColumnInfo.ensure_subclass(column)
        super().add_column(column)
    # --- Internal Helpers ---
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
                column._tables.discard(self)
                self._column_dict.pop(name, None)

        # Add new ones
        for column in new_columns:
            self.validate_new_column(column)
            self._column_dict[column.name] = column
            column._tables.add(self)

        self._columns = new_columns
    @staticmethod
    def validate_columns(columns: Union[Iterable[SQLColumnInfoBase], Unknown]) -> List[SQLColumnInfo]:
        if is_undetermined(columns):
            return []
        validated_columns = SQLTableInfoBase.validate_columns(columns)
        actual_columns = [SQLColumnInfo.ensure_subclass(col) for col in validated_columns]
        return actual_columns

