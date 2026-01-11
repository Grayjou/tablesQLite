Usage Guide
===========

This guide covers common usage patterns and advanced features of tablesQLite.

Table Management
----------------

Creating Tables
~~~~~~~~~~~~~~~

Generate SQL to create a table:

.. code-block:: python

   from tablesqlite import SQLColumnInfo, SQLTableInfo

   table = SQLTableInfo(
       name="products",
       columns=[
           SQLColumnInfo("id", "INTEGER", primary_key=True),
           SQLColumnInfo("name", "TEXT", not_null=True),
           SQLColumnInfo("price", "REAL", not_null=True),
           SQLColumnInfo("stock", "INTEGER", default_value=0),
       ]
   )

   query, params = table.create_query()

The ``create_query()`` method returns a tuple of ``(query_string, parameters)``.

Dropping Tables
~~~~~~~~~~~~~~~

Generate SQL to drop a table:

.. code-block:: python

   # Drop table unconditionally
   query, params = table.drop_query()
   # DROP TABLE "products"

   # Drop table only if it exists
   query, params = table.drop_query(if_exists=True)
   # DROP TABLE IF EXISTS "products"

Renaming Tables
~~~~~~~~~~~~~~~

Generate SQL to rename a table:

.. code-block:: python

   query, params = table.rename_query("new_products")
   # ALTER TABLE "products" RENAME TO "new_products"

Column Management
-----------------

Adding Columns
~~~~~~~~~~~~~~

Add a new column to an existing table:

.. code-block:: python

   new_column = SQLColumnInfo("description", "TEXT")
   query, params = table.add_column_query(new_column)
   # ALTER TABLE "products" ADD COLUMN "description" TEXT

Note: SQLite has limitations on adding columns with certain constraints.

Dropping Columns
~~~~~~~~~~~~~~~~

Remove a column from a table:

.. code-block:: python

   query, params = table.drop_column_query("description")
   # ALTER TABLE "products" DROP COLUMN "description"

Note: SQLite version 3.35.0+ is required for dropping columns.

Renaming Columns
~~~~~~~~~~~~~~~~

Rename a column:

.. code-block:: python

   query, params = table.rename_column_query("price", "unit_price")
   # ALTER TABLE "products" RENAME COLUMN "price" TO "unit_price"

Constraints
-----------

NOT NULL Constraint
~~~~~~~~~~~~~~~~~~~

Ensure a column cannot contain NULL values:

.. code-block:: python

   column = SQLColumnInfo("name", "TEXT", not_null=True)

DEFAULT Constraint
~~~~~~~~~~~~~~~~~~

Specify a default value for a column:

.. code-block:: python

   # Simple default value
   column = SQLColumnInfo("quantity", "INTEGER", default_value=1)

   # SQL function as default
   column = SQLColumnInfo("created_at", "DATETIME", 
                         default_value="CURRENT_TIMESTAMP")

PRIMARY KEY Constraint
~~~~~~~~~~~~~~~~~~~~~~

Define a primary key:

.. code-block:: python

   # Single column primary key
   column = SQLColumnInfo("id", "INTEGER", primary_key=True)
   # This automatically adds AUTOINCREMENT for INTEGER PRIMARY KEY

UNIQUE Constraint
~~~~~~~~~~~~~~~~~

Ensure column values are unique:

.. code-block:: python

   column = SQLColumnInfo("email", "TEXT", unique=True)

CHECK Constraint
~~~~~~~~~~~~~~~~

Add a custom validation constraint:

.. code-block:: python

   from expressQL import parse_condition

   column = SQLColumnInfo(
       "age",
       "INTEGER",
       check=parse_condition("age >= 0 AND age <= 150")
   )

FOREIGN KEY Constraint
~~~~~~~~~~~~~~~~~~~~~~

Define relationships between tables:

.. code-block:: python

   # Single-column foreign key
   column = SQLColumnInfo(
       "category_id",
       "INTEGER",
       foreign_key={"table": "categories", "column": "id"}
   )

   # Multi-column foreign key (table-level)
   table = SQLTableInfo(
       name="order_items",
       columns=[
           SQLColumnInfo("order_id", "INTEGER"),
           SQLColumnInfo("product_id", "INTEGER"),
       ],
       foreign_keys=[
           {
               "columns": ["order_id", "product_id"],
               "ref_table": "orders",
               "ref_columns": ["id", "product_id"]
           }
       ]
   )

Schema Parsing
--------------

Parse SQL Schema
~~~~~~~~~~~~~~~~

Convert SQL schema strings back into Python objects:

.. code-block:: python

   from tablesqlite import SQLTableInfo

   schema = """
   CREATE TABLE employees (
       id INTEGER PRIMARY KEY,
       first_name TEXT NOT NULL,
       last_name TEXT NOT NULL,
       department_id INTEGER,
       salary REAL DEFAULT 0.0,
       FOREIGN KEY (department_id) REFERENCES departments(id)
   );
   """

   table = SQLTableInfo.from_sql_schema(schema)

   # Access table information
   print(f"Table name: {table.name}")
   for column in table.columns:
       print(f"Column: {column.name} ({column.data_type})")

Utility Functions
-----------------

Enum Conversion
~~~~~~~~~~~~~~~

Convert values to IntEnum types:

.. code-block:: python

   from enum import IntEnum
   from tablesqlite import convert_enum_value

   class Status(IntEnum):
       PENDING = 1
       ACTIVE = 2
       COMPLETED = 3

   # Convert from string
   status = convert_enum_value("2", Status)  # Status.ACTIVE

   # Convert from int
   status = convert_enum_value(1, Status)    # Status.PENDING

Foreign Key Validation
~~~~~~~~~~~~~~~~~~~~~~

Validate foreign key relationships across tables:

.. code-block:: python

   from tablesqlite import validate_foreign_keys, SQLTableInfo, SQLColumnInfo

   users = SQLTableInfo("users", [
       SQLColumnInfo("id", "INTEGER", primary_key=True)
   ])
   
   posts = SQLTableInfo("posts", [
       SQLColumnInfo("id", "INTEGER", primary_key=True),
       SQLColumnInfo("user_id", "INTEGER",
                    foreign_key={"table": "users", "column": "id"})
   ])

   tables = {"users": users, "posts": posts}
   errors = validate_foreign_keys(posts, tables)
   
   if errors:
       print("Foreign key errors:", errors)

Schema Migration
~~~~~~~~~~~~~~~~

Generate migration statements between two table versions:

.. code-block:: python

   from tablesqlite import generate_migration, SQLTableInfo, SQLColumnInfo

   # Old table schema
   old_table = SQLTableInfo("users", [
       SQLColumnInfo("id", "INTEGER", primary_key=True),
       SQLColumnInfo("name", "TEXT")
   ])

   # New table schema with additional column
   new_table = SQLTableInfo("users", [
       SQLColumnInfo("id", "INTEGER", primary_key=True),
       SQLColumnInfo("name", "TEXT"),
       SQLColumnInfo("email", "TEXT")
   ])

   # Generate migration statements
   migrations = generate_migration(old_table, new_table)
   for sql, params in migrations:
       print(sql)
   # Output: ALTER TABLE "users" ADD COLUMN "email" TEXT

Best Practices
--------------

1. **Always use parameterized queries**: The ``create_query()`` and similar methods return both SQL and parameters. Use these with parameterized queries to prevent SQL injection.

2. **Validate foreign keys**: Use ``validate_foreign_keys()`` before deploying schema changes to catch reference errors early.

3. **Test schema changes**: Generate migration statements with ``generate_migration()`` and review them before applying to production databases.

4. **Use type hints**: The library is fully typed. Enable type checking with mypy to catch errors at development time.

5. **Consider SQLite limitations**: Be aware of SQLite's constraints on ALTER TABLE operations, especially when adding columns with certain constraints.
