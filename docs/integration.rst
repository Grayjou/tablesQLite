Integration with recordsQL
==========================

tablesQLite focuses on DDL (Data Definition Language) operations, while `recordsQL <https://pypi.org/project/recordsQL>`_ 
handles DML (Data Manipulation Language) operations like INSERT, UPDATE, SELECT, and DELETE. 
Together, they provide a complete solution for SQLite database management.

Overview
--------

tablesQLite provides:

* Table schema definition
* SQL DDL generation (CREATE TABLE, ALTER TABLE, DROP TABLE)
* Schema parsing

recordsQL provides:

* INSERT, UPDATE, SELECT, DELETE operations
* Query building with conditions
* Integration support for tablesQLite

Installation
------------

To use both libraries together:

.. code-block:: bash

   pip install tablesqlite recordsQL

Basic Integration
-----------------

The recordsQL library provides an integration module that adds DML methods to ``SQLTableInfo``:

.. code-block:: python

   from tablesqlite import SQLColumnInfo, SQLTableInfo
   from recordsQL.integrations.tablesqlite import add_query_methods

   # Enable integration
   add_query_methods()

   # Define your table
   table = SQLTableInfo(
       name="users",
       columns=[
           SQLColumnInfo("id", "INTEGER", primary_key=True),
           SQLColumnInfo("name", "TEXT", not_null=True),
           SQLColumnInfo("email", "TEXT", unique=True),
       ]
   )

   # Now you can use DML methods
   # Insert data
   query, params = table.insert_query({"name": "John", "email": "john@example.com"})

   # Select data
   query, params = table.select_query(columns=["name", "email"])

   # Update data
   from expressQL import parse_condition
   condition = parse_condition("id = 1")
   query, params = table.update_query({"name": "Jane"}, condition)

   # Delete data
   query, params = table.delete_query(condition)

Complete Example
----------------

Here's a complete example showing both DDL and DML operations:

.. code-block:: python

   import sqlite3
   from tablesqlite import SQLColumnInfo, SQLTableInfo
   from recordsQL.integrations.tablesqlite import add_query_methods
   from expressQL import parse_condition

   # Enable recordsQL integration
   add_query_methods()

   # Create a database connection
   conn = sqlite3.connect(":memory:")
   cursor = conn.cursor()

   # Define the table schema (DDL with tablesQLite)
   users_table = SQLTableInfo(
       name="users",
       columns=[
           SQLColumnInfo("id", "INTEGER", primary_key=True),
           SQLColumnInfo("name", "TEXT", not_null=True),
           SQLColumnInfo("email", "TEXT", unique=True),
           SQLColumnInfo("age", "INTEGER"),
       ]
   )

   # Create the table
   create_query, create_params = users_table.create_query()
   cursor.execute(create_query, create_params)

   # Insert data (DML with recordsQL integration)
   insert_query, insert_params = users_table.insert_query({
       "name": "Alice",
       "email": "alice@example.com",
       "age": 30
   })
   cursor.execute(insert_query, insert_params)

   insert_query, insert_params = users_table.insert_query({
       "name": "Bob",
       "email": "bob@example.com",
       "age": 25
   })
   cursor.execute(insert_query, insert_params)

   # Select data
   select_query, select_params = users_table.select_query(
       columns=["name", "age"]
   )
   results = cursor.execute(select_query, select_params).fetchall()
   print("Users:", results)

   # Update data
   update_condition = parse_condition("name = 'Alice'")
   update_query, update_params = users_table.update_query(
       {"age": 31},
       update_condition
   )
   cursor.execute(update_query, update_params)

   # Delete data
   delete_condition = parse_condition("age < 30")
   delete_query, delete_params = users_table.delete_query(delete_condition)
   cursor.execute(delete_query, delete_params)

   # Verify changes
   select_query, select_params = users_table.select_query()
   results = cursor.execute(select_query, select_params).fetchall()
   print("Remaining users:", results)

   conn.close()

Schema Evolution
----------------

When evolving your schema, use tablesQLite's migration utilities alongside recordsQL:

.. code-block:: python

   from tablesqlite import SQLTableInfo, SQLColumnInfo, generate_migration
   from recordsQL.integrations.tablesqlite import add_query_methods

   add_query_methods()

   # Old schema
   old_users = SQLTableInfo(
       name="users",
       columns=[
           SQLColumnInfo("id", "INTEGER", primary_key=True),
           SQLColumnInfo("name", "TEXT", not_null=True),
       ]
   )

   # New schema with additional column
   new_users = SQLTableInfo(
       name="users",
       columns=[
           SQLColumnInfo("id", "INTEGER", primary_key=True),
           SQLColumnInfo("name", "TEXT", not_null=True),
           SQLColumnInfo("email", "TEXT"),
       ]
   )

   # Generate migration
   migrations = generate_migration(old_users, new_users)
   for sql, params in migrations:
       print(f"Migration: {sql}")
       # Execute with your database connection
       # cursor.execute(sql, params)

Additional Resources
--------------------

* `recordsQL Documentation <https://github.com/Grayjou/recordsQL>`_
* `Complete Integration Example <https://github.com/Grayjou/tablesQLite/blob/main/INTEGRATION_EXAMPLE.md>`_

Best Practices
--------------

1. **Separate concerns**: Use tablesQLite for schema definition and DDL, recordsQL for data operations.

2. **Enable integration once**: Call ``add_query_methods()`` once at the start of your application.

3. **Type safety**: Both libraries provide full type hints. Use them to catch errors at development time.

4. **Transaction management**: Use proper transaction management when performing multiple operations:

   .. code-block:: python

      try:
          cursor.execute(create_query, create_params)
          cursor.execute(insert_query, insert_params)
          conn.commit()
      except Exception as e:
          conn.rollback()
          raise

5. **Test migrations**: Always test schema migrations in a development environment before applying to production.
