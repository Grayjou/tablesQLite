# tablesQLite

[![PyPI version](https://badge.fury.io/py/tablesqlite.svg)](https://badge.fury.io/py/tablesqlite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Typing: typed](https://img.shields.io/badge/typing-typed-green.svg)](https://www.python.org/dev/peps/pep-0561/)

A declarative SQLite table builder and schema manager for Python. Define your database tables with rich column constraints, generate SQL DDL statements, and parse existing schemas back into Python objects.

## Features

- **Declarative Table Definitions**: Define tables using `SQLTableInfo` and `SQLColumnInfo` classes with full constraint support
- **Rich Column Constraints**: Support for `NOT NULL`, `DEFAULT`, `CHECK`, `UNIQUE`, `PRIMARY KEY`, and `FOREIGN KEY` constraints
- **SQL Generation**: Generate `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE` SQL statements
- **Schema Parsing**: Parse existing SQL schema strings back into Python objects
- **Type Safety**: Full type hints throughout the codebase
- **Integration Ready**: Seamlessly integrates with [recordsQL](https://pypi.org/project/recordsQL) for DML operations
- **Utility Functions**: Helper functions for type conversion, foreign key validation, and schema migrations

## Installation

```bash
pip install tablesqlite
```

## Quick Start

### Define a Table

```python
from tablesqlite import SQLColumnInfo, SQLTableInfo
from expressQL import parse_condition

# Define columns with constraints
columns = [
    SQLColumnInfo("id", "INTEGER", primary_key=True),
    SQLColumnInfo("name", "TEXT", not_null=True),
    SQLColumnInfo("email", "TEXT", unique=True),
    SQLColumnInfo(
        "age",
        "INTEGER",
        not_null=True,
        check=parse_condition("age >= 18")
    ),
    SQLColumnInfo("balance", "REAL", default_value=0.0),
    SQLColumnInfo("created_at", "DATETIME", default_value="CURRENT_TIMESTAMP"),
]

# Create table definition
users_table = SQLTableInfo(name="users", columns=columns)

# Generate CREATE TABLE SQL
query, params = users_table.create_query()
print(query)
```

Output:

```sql
CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "email" TEXT UNIQUE,
    "age" INTEGER NOT NULL CHECK (age >= 18),
    "balance" REAL DEFAULT 0.0,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Parse Existing Schema

```python
from tablesqlite import SQLTableInfo

schema = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER CHECK (age >= 18)
);
"""

table_info = SQLTableInfo.from_sql_schema(schema)
print(f"Table: {table_info.name}")
for col in table_info.columns:
    print(f"  - {col.name}: {col.data_type}")
```

### Foreign Key Support

```python
from tablesqlite import SQLColumnInfo, SQLTableInfo

# Single-column foreign key (inline)
owner_id_column = SQLColumnInfo(
    "owner_id",
    "INTEGER",
    not_null=True,
    foreign_key={"table": "owners", "column": "id"}
)

# Multi-column foreign key (table-level)
orders_table = SQLTableInfo(
    name="orders",
    columns=[
        SQLColumnInfo("id", "INTEGER", primary_key=True),
        SQLColumnInfo("customer_id", "INTEGER", not_null=True),
        SQLColumnInfo("store_id", "INTEGER", not_null=True),
    ],
    foreign_keys=[
        {
            "columns": ["customer_id", "store_id"],
            "ref_table": "customer_stores",
            "ref_columns": ["customer_id", "store_id"]
        }
    ]
)
```

### Column Operations

```python
from tablesqlite import SQLColumnInfo, SQLTableInfo

table = SQLTableInfo(name="users", columns=[
    SQLColumnInfo("id", "INTEGER", primary_key=True),
    SQLColumnInfo("name", "TEXT"),
])

# Add a new column
new_column = SQLColumnInfo("email", "TEXT", unique=True)
query, params = table.add_column_query(new_column)
# ALTER TABLE "users" ADD COLUMN "email" TEXT UNIQUE

# Drop a column
query, params = table.drop_column_query("name")
# ALTER TABLE "users" DROP COLUMN "name"

# Rename a column
query, params = table.rename_column_query("email", "user_email")
# ALTER TABLE "users" RENAME COLUMN "email" TO "user_email"
```

### Utility Functions

tablesQLite provides helpful utility functions for common tasks:

```python
from enum import IntEnum
from tablesqlite import (
    convert_enum_value,
    validate_foreign_keys,
    generate_migration,
    SQLTableInfo,
    SQLColumnInfo
)

# Type conversion helper for IntEnum
class Status(IntEnum):
    PENDING = 1
    ACTIVE = 2
    COMPLETED = 3

status = convert_enum_value("2", Status)  # Returns Status.ACTIVE
status = convert_enum_value(1, Status)    # Returns Status.PENDING

# Validate foreign key relationships
users = SQLTableInfo("users", [SQLColumnInfo("id", "INTEGER", primary_key=True)])
posts = SQLTableInfo("posts", [
    SQLColumnInfo("id", "INTEGER", primary_key=True),
    SQLColumnInfo("user_id", "INTEGER", foreign_key={"table": "users", "column": "id"})
])

tables = {"users": users, "posts": posts}
errors = validate_foreign_keys(posts, tables)
if errors:
    print("Foreign key errors:", errors)

# Generate migration statements
old_table = SQLTableInfo("users", [
    SQLColumnInfo("id", "INTEGER", primary_key=True),
    SQLColumnInfo("name", "TEXT")
])
new_table = SQLTableInfo("users", [
    SQLColumnInfo("id", "INTEGER", primary_key=True),
    SQLColumnInfo("name", "TEXT"),
    SQLColumnInfo("email", "TEXT")
])

migrations = generate_migration(old_table, new_table)
for sql, params in migrations:
    print(sql)
# Output: ALTER TABLE "users" ADD COLUMN "email" TEXT
```

## API Reference

### SQLColumnInfo

Represents a column definition with full constraint support.

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Column name |
| `data_type` | `str` | required | SQL data type (e.g., "INTEGER", "TEXT") |
| `not_null` | `bool` | `False` | NOT NULL constraint |
| `default_value` | `str \| int \| float \| Unknown` | `unknown` | Default value |
| `primary_key` | `bool` | `False` | PRIMARY KEY constraint |
| `cid` | `int \| Unknown` | `unknown` | Column ID |
| `unique` | `bool` | `False` | UNIQUE constraint |
| `foreign_key` | `dict \| None` | `None` | Foreign key definition |
| `check` | `SQLCondition \| None` | `None` | CHECK constraint |

### SQLTableInfo

Represents a table definition with columns and constraints.

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | required | Table name |
| `columns` | `Iterable[SQLColumnInfo]` | `unknown` | Table columns |
| `database_path` | `str \| Unknown` | `unknown` | Database file path |
| `foreign_keys` | `list[dict]` | `None` | Table-level foreign keys |

**Key Methods:**

- `create_query()` - Generate CREATE TABLE SQL
- `drop_query(if_exists=False)` - Generate DROP TABLE SQL
- `rename_query(new_name)` - Generate RENAME TABLE SQL
- `add_column_query(column)` - Generate ADD COLUMN SQL
- `drop_column_query(column_name)` - Generate DROP COLUMN SQL
- `rename_column_query(old_name, new_name)` - Generate RENAME COLUMN SQL
- `from_sql_schema(schema)` - Parse SQL schema string into SQLTableInfo

## Integration with recordsQL

tablesQLite focuses on DDL (Data Definition Language) operations. For DML (Data Manipulation Language) operations like INSERT, UPDATE, SELECT, and DELETE, use [recordsQL](https://pypi.org/project/recordsQL).

See [INTEGRATION_EXAMPLE.md](INTEGRATION_EXAMPLE.md) for a complete example of using tablesQLite with recordsQL.

```python
from recordsQL.integrations.tablesqlite import add_query_methods

# Add insert/update/select/delete methods to SQLTableInfo
add_query_methods()

# Now you can use:
# table_info.insert_query(data)
# table_info.select_query(columns)
# table_info.update_query(data, condition)
# table_info.delete_query(condition)
```

## Dependencies

- [expressQL](https://pypi.org/project/expressQL) - SQL expression builder
- [sortedcontainers](https://pypi.org/project/sortedcontainers) - Sorted container types

## Documentation

Full documentation is available online and can be built locally.

### Online Documentation

Visit the [full documentation](https://github.com/Grayjou/tablesqlite#readme) for detailed guides and API reference.

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install tablesqlite[docs]

# Build HTML documentation
cd docs
make html

# Open docs/_build/html/index.html in your browser
```

The documentation includes:
- Installation guide
- Quick start tutorial
- Comprehensive usage guide
- Complete API reference
- Integration examples with recordsQL

## Development

```bash
# Install development dependencies
pip install tablesqlite[dev]

# Run linting
ruff check .

# Run type checking
mypy tablesqlite
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.
