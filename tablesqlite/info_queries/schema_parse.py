import re
from typing import List
from ..objects import SQLTableInfoBase, SQLColumnInfoBase
from expressql import parse_condition, parse_expression
def parse_sql_schema(schema: str) -> SQLTableInfoBase:
    schema = schema.strip().rstrip(';')
    if not schema.upper().startswith("CREATE TABLE"):
        raise ValueError("Schema must start with CREATE TABLE")

    match = re.match(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)", schema, re.IGNORECASE)
    if not match:
        raise ValueError("Could not parse table name")
    table_name = match.group(1).strip('"')

    inside = schema[schema.find("(")+1 : schema.rfind(")")]
    parts = re.split(r",(?![^()]*\))", inside)

    column_defs = []
    table_constraints = []

    for part in parts:
        part = part.strip()
        if re.match(r"^(PRIMARY KEY|UNIQUE|FOREIGN KEY|CHECK)", part, re.IGNORECASE):
            table_constraints.append(part)
        else:
            column_defs.append(part)

    columns: List[SQLColumnInfoBase] = []
    foreign_keys = []

    for col_def in column_defs:
        tokens = re.split(r"\s+", col_def, maxsplit=2)
        if len(tokens) < 2:
            continue

        name = tokens[0].strip('"')
        data_type = tokens[1].upper()
        constraints = tokens[2] if len(tokens) == 3 else ""

        not_null = re.search(r"\bNOT NULL\b", constraints, re.IGNORECASE) is not None
        primary_key = re.search(r"\bPRIMARY KEY\b", constraints, re.IGNORECASE) is not None
        unique = re.search(r"\bUNIQUE\b", constraints, re.IGNORECASE) is not None


        default_value = None
        match_default = re.search(r"\bDEFAULT\s+((?:'[^']*'|\"[^\"]*\"|\S+))", constraints, re.IGNORECASE)
        if match_default:
            try:
                s = match_default.group(1)

                if s.upper() in ("TRUE", "FALSE"):
                    default_value = s.upper() == "TRUE"
                else:
                    default_value = parse_expression(s)

            except Exception as e:
                raise ValueError(f"Invalid DEFAULT value: {match_default.group(1)}\nError: {e}")

        fk_match = re.search(r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)", constraints, re.IGNORECASE)
        foreign_key = None
        if fk_match:
            foreign_key = {"table": fk_match.group(1), "column": fk_match.group(2)}

        check_condition = None
        check_match = re.search(r"CHECK\s*\((.*?)\)", constraints, re.IGNORECASE)
        if check_match:
            try:
                check_condition = parse_condition(check_match.group(1))
            except Exception as e:
                raise ValueError(f"Invalid CHECK condition: {check_match.group(1)}\nError: {e}")

        columns.append(SQLColumnInfoBase(
            name=name,
            data_type=data_type,
            not_null=not_null,
            default_value=default_value,
            primary_key=primary_key,
            unique=unique,
            foreign_key=foreign_key,
            check=check_condition
        ))

    for constraint in table_constraints:
        if constraint.upper().startswith("PRIMARY KEY"):
            pk_cols = re.findall(r"\((.*?)\)", constraint)
            if pk_cols:
                pk_names = [name.strip().strip('"') for name in pk_cols[0].split(',')]
                for col in columns:
                    if col.name in pk_names:
                        col.primary_key = True

        elif constraint.upper().startswith("FOREIGN KEY"):
            col_match = re.search(
                r"FOREIGN KEY\s*\((.*?)\)\s*REFERENCES\s+(\w+)\s*\((.*?)\)",
                constraint,
                re.IGNORECASE
            )
            if col_match:
                raw_local = col_match.group(1)
                raw_ref   = col_match.group(3)
                local_cols = [
                    c.strip().strip('"').strip("'")
                    for c in raw_local.split(",")
                ]
                ref_table  = col_match.group(2).strip()
                ref_cols   = [
                    c.strip().strip('"').strip("'")
                    for c in raw_ref.split(",")
                ]
                foreign_keys.append({
                    "columns":      local_cols,
                    "ref_table":    ref_table,
                    "ref_columns":  ref_cols
                })


    return SQLTableInfoBase(name=table_name, columns=columns, foreign_keys=foreign_keys)
def main(writer = None):
    if writer is None:
        register = print
    else:
        register = writer.write_words_line
    read = "CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, species TEXT DEFAULT 'Unknown', age INTEGER DEFAULT 0, vaccinated BOOLEAN DEFAULT False, owner_id INTEGER NOT NULL, FOREIGN KEY (owner_id) REFERENCES owners(id))"
    table_info = parse_sql_schema(read)
    register(f"Table Name: {table_info.name}")
    register(table_info.columns)
    register("Columns:")
    for col_ in table_info.columns:
        register(col_.creation_str())
    from expressql import cols
    debt, income, interest = cols("debt", "income", "interest")
    condition = (debt*interest) < (income*12)
    register(f"Condition: {condition.sql_string()}")
    schema = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        age INTEGER NOT NULL CHECK (age >= 18 AND age < 100),
        income REAL CHECK (income > 0)
    );
    """

    parsed_table = parse_sql_schema(schema)
    for col in parsed_table.columns:
        register(f"{col.name}: {col.creation_str()}")

    