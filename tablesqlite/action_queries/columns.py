from ..objects import SQLTableInfoBase, SQLColumnInfoBase
from ..objects.generic import ensure_quoted

def _extract_table_name(table, check=None):
    if not isinstance(table, (str, SQLTableInfoBase)):
        raise TypeError("table must be a string or an instance of SQLTableInfoBase")
    if isinstance(table, SQLTableInfoBase):
        if check:
            check(table)
        return table.name
    return table.strip('"').strip("'")

def add_column_query(table: SQLTableInfoBase | str, column: SQLColumnInfoBase, check_if_possible: bool = False) -> tuple[str, list]:
    if not isinstance(column, SQLColumnInfoBase):
        raise TypeError("column must be an instance of SQLColumnInfoBase")

    def check(table_obj):
        if check_if_possible:
            table_obj.validate_new_column(column)

    table_name = _extract_table_name(table, check)
    query = f"ALTER TABLE {ensure_quoted(table_name)} ADD COLUMN {column.creation_str()}"
    return query, []

def drop_column_query(table: SQLTableInfoBase | str, column_name: str, check_if_possible: bool = False) -> tuple[str, list]:
    def check(table_obj):
        if check_if_possible and column_name not in table_obj.column_dict:
            raise ValueError(f"Column '{column_name}' does not exist in table '{table_obj.name}'")

    table_name = _extract_table_name(table, check)
    query = f"ALTER TABLE {ensure_quoted(table_name)} DROP COLUMN {ensure_quoted(column_name)}"
    return query, []

def rename_column_query(table: SQLTableInfoBase | str, old_name: str, new_name: str, check_if_possible: bool = False) -> tuple[str, list]:
    def check(table_obj):
        if not check_if_possible:
            return
        if old_name not in table_obj.column_dict:
            raise ValueError(f"Column '{old_name}' does not exist in table '{table_obj.name}'")
        if new_name in table_obj.column_dict:
            raise ValueError(f"Column '{new_name}' already exists in table '{table_obj.name}'")

    table_name = _extract_table_name(table, check)
    query = f"ALTER TABLE {ensure_quoted(table_name)} RENAME COLUMN {ensure_quoted(old_name)} TO {ensure_quoted(new_name)}"
    return query, []
