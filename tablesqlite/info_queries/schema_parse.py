"""SQL schema parsing utilities.

This module provides functions for parsing SQL CREATE TABLE statements
into SQLTableInfoBase objects.
"""

from __future__ import annotations

import re
from typing import Any

from expressql import parse_condition, parse_expression

from ..objects import SQLColumnInfoBase, SQLTableInfoBase


def parse_sql_schema(schema: str) -> SQLTableInfoBase:
    """Parse a SQL CREATE TABLE statement into a SQLTableInfoBase.

    Args:
        schema: The SQL CREATE TABLE statement to parse.

    Returns:
        A SQLTableInfoBase instance representing the parsed table.

    Raises:
        ValueError: If the schema is invalid or cannot be parsed.
    """
    schema = schema.strip().rstrip(";")
    if not schema.upper().startswith("CREATE TABLE"):
        raise ValueError("Schema must start with CREATE TABLE")

    match = re.match(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)",
        schema,
        re.IGNORECASE,
    )
    if not match:
        raise ValueError("Could not parse table name")
    table_name = match.group(1).strip('"')

    inside = schema[schema.find("(") + 1 : schema.rfind(")")]
    parts = re.split(r",(?![^()]*\))", inside)

    column_defs: list[str] = []
    table_constraints: list[str] = []

    for part in parts:
        part = part.strip()
        if re.match(r"^(PRIMARY KEY|UNIQUE|FOREIGN KEY|CHECK)", part, re.IGNORECASE):
            table_constraints.append(part)
        else:
            column_defs.append(part)

    columns: list[SQLColumnInfoBase] = []
    foreign_keys: list[dict[str, Any]] = []

    for col_def in column_defs:
        tokens = re.split(r"\s+", col_def, maxsplit=2)
        if len(tokens) < 2:
            continue

        name = tokens[0].strip('"')
        data_type = tokens[1].upper()
        constraints = tokens[2] if len(tokens) == 3 else ""

        not_null = (
            re.search(r"\bNOT NULL\b", constraints, re.IGNORECASE) is not None
        )
        primary_key = (
            re.search(r"\bPRIMARY KEY\b", constraints, re.IGNORECASE) is not None
        )
        unique = re.search(r"\bUNIQUE\b", constraints, re.IGNORECASE) is not None

        default_value: str | int | float | bool | None = None
        match_default = re.search(
            r"\bDEFAULT\s+((?:'[^']*'|\"[^\"]*\"|\S+))",
            constraints,
            re.IGNORECASE,
        )
        if match_default:
            try:
                s = match_default.group(1)

                if s.upper() in ("TRUE", "FALSE"):
                    default_value = s.upper() == "TRUE"
                else:
                    default_value = parse_expression(s)

            except Exception as e:
                raise ValueError(
                    f"Invalid DEFAULT value: {match_default.group(1)}\nError: {e}"
                ) from e

        fk_match = re.search(
            r"REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)",
            constraints,
            re.IGNORECASE,
        )
        foreign_key: dict[str, str] | None = None
        if fk_match:
            foreign_key = {
                "table": fk_match.group(1),
                "column": fk_match.group(2),
            }

        check_condition = None
        check_match = re.search(r"CHECK\s*\((.*?)\)", constraints, re.IGNORECASE)
        if check_match:
            try:
                check_condition = parse_condition(check_match.group(1))
            except Exception as e:
                raise ValueError(
                    f"Invalid CHECK condition: {check_match.group(1)}\nError: {e}"
                ) from e

        columns.append(
            SQLColumnInfoBase(
                name=name,
                data_type=data_type,
                not_null=not_null,
                default_value=default_value,
                primary_key=primary_key,
                unique=unique,
                foreign_key=foreign_key,
                check=check_condition,
            )
        )

    for constraint in table_constraints:
        if constraint.upper().startswith("PRIMARY KEY"):
            pk_cols = re.findall(r"\((.*?)\)", constraint)
            if pk_cols:
                pk_names = [
                    name.strip().strip('"') for name in pk_cols[0].split(",")
                ]
                for col in columns:
                    if col.name in pk_names:
                        col.primary_key = True

        elif constraint.upper().startswith("FOREIGN KEY"):
            col_match = re.search(
                r"FOREIGN KEY\s*\((.*?)\)\s*REFERENCES\s+(\w+)\s*\((.*?)\)",
                constraint,
                re.IGNORECASE,
            )
            if col_match:
                raw_local = col_match.group(1)
                raw_ref = col_match.group(3)
                local_cols = [
                    c.strip().strip('"').strip("'") for c in raw_local.split(",")
                ]
                ref_table = col_match.group(2).strip()
                ref_cols = [
                    c.strip().strip('"').strip("'") for c in raw_ref.split(",")
                ]
                foreign_keys.append(
                    {
                        "columns": local_cols,
                        "ref_table": ref_table,
                        "ref_columns": ref_cols,
                    }
                )

    return SQLTableInfoBase(
        name=table_name, columns=columns, foreign_keys=foreign_keys
    )
