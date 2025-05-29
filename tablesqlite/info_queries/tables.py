#pairs are in the form (query, parameters)
from ..validation import validate_name

def validate_table_name(table_name_pos:int = 0, already_validated_pos:int = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            table_name = args[table_name_pos]
            if already_validated_pos is not None:
                already_validated = args[already_validated_pos]
                validate = already_validated if isinstance(already_validated, bool) else False
            else:
                validate =  True
            if validate:
                validate_name(table_name, allow_dot= False)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_all_tables_query(*args, **kwargs):
    """
    Returns a SQL query to retrieve all table names from the SQLite database.
    """
    return "SELECT name FROM sqlite_master WHERE type='table'", []

@validate_table_name(0, 1)
def get_table_info_query(table_name, already_validated=False):
    """
    Returns a SQL query to retrieve information about a specific table in the SQLite database.

    Args:
        table_name (str): The name of the table to retrieve information for.

    Returns:
        tuple: A tuple containing the SQL query and a list of parameters.
    """
    return f"PRAGMA table_info('{table_name}')", []

@validate_table_name(0, 1)
def count_rows_query(table_name, already_validated=False):
    """
    Returns a SQL query to count the number of rows in a specific table.

    Args:
        table_name (str): The name of the table to count rows for.

    Returns:
        tuple: A tuple containing the SQL query and a list of parameters.
    """
    return f"SELECT COUNT(*) FROM '{table_name}'", []