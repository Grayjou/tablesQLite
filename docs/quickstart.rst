Quick Start
===========

This guide will help you get started with tablesQLite quickly.

Basic Usage
-----------

Define a Simple Table
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tablesqlite import SQLColumnInfo, SQLTableInfo

   # Define columns
   columns = [
       SQLColumnInfo("id", "INTEGER", primary_key=True),
       SQLColumnInfo("name", "TEXT", not_null=True),
       SQLColumnInfo("email", "TEXT", unique=True),
   ]

   # Create table definition
   users_table = SQLTableInfo(name="users", columns=columns)

   # Generate CREATE TABLE SQL
   query, params = users_table.create_query()
   print(query)

This produces:

.. code-block:: sql

   CREATE TABLE "users" (
       "id" INTEGER PRIMARY KEY AUTOINCREMENT,
       "name" TEXT NOT NULL,
       "email" TEXT UNIQUE
   );

Adding Constraints
~~~~~~~~~~~~~~~~~~

tablesQLite supports various column constraints:

.. code-block:: python

   from tablesqlite import SQLColumnInfo, SQLTableInfo
   from expressQL import parse_condition

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
       SQLColumnInfo(
           "created_at",
           "DATETIME",
           default_value="CURRENT_TIMESTAMP"
       ),
   ]

   users_table = SQLTableInfo(name="users", columns=columns)

Parse Existing Schema
~~~~~~~~~~~~~~~~~~~~~

You can parse an existing SQL schema string into Python objects:

.. code-block:: python

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

Foreign Keys
~~~~~~~~~~~~

Define foreign key relationships:

.. code-block:: python

   from tablesqlite import SQLColumnInfo, SQLTableInfo

   # Single-column foreign key (inline)
   posts_columns = [
       SQLColumnInfo("id", "INTEGER", primary_key=True),
       SQLColumnInfo("title", "TEXT", not_null=True),
       SQLColumnInfo(
           "user_id",
           "INTEGER",
           not_null=True,
           foreign_key={"table": "users", "column": "id"}
       ),
   ]

   posts_table = SQLTableInfo(name="posts", columns=posts_columns)

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

Column Operations
~~~~~~~~~~~~~~~~~

Modify table structure:

.. code-block:: python

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

Next Steps
----------

* Learn more about :doc:`usage` patterns
* Explore the :doc:`api` reference
* Check out :doc:`integration` with recordsQL
