from ..objects import SQLTableInfoBase

def _extract_table_name(table):
    if not isinstance(table, (str, SQLTableInfoBase)):
        raise TypeError("table must be a string or an instance of SQLTableInfoBase")
    if isinstance(table, SQLTableInfoBase):
        return table.name
    return table.strip('"').strip("'")


def create_table_query( t: SQLTableInfoBase):
    return t.creation_str(), []

def drop_table_query(table: SQLTableInfoBase | str, check_if_exists: bool = False) -> tuple[str, list]:
    table_name = _extract_table_name(table)
    if check_if_exists:
        query = f"DROP TABLE IF EXISTS {table_name}"
    else:
        query = f"DROP TABLE {table_name}"
    return query, []

def rename_table_query(old_name: str, new_name: str, check_if_exists: bool = False) -> tuple[str, list]:
    if check_if_exists:
        query = f"ALTER TABLE {old_name} RENAME TO IF EXISTS {new_name}"
    else:
        query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
    return query, []