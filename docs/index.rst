Welcome to tablesQLite's documentation!
========================================

**tablesQLite** is a declarative SQLite table builder and schema manager for Python. 
Define your database tables with rich column constraints, generate SQL DDL statements, 
and parse existing schemas back into Python objects.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   usage
   api
   integration

Features
--------

* **Declarative Table Definitions**: Define tables using ``SQLTableInfo`` and ``SQLColumnInfo`` classes with full constraint support
* **Rich Column Constraints**: Support for ``NOT NULL``, ``DEFAULT``, ``CHECK``, ``UNIQUE``, ``PRIMARY KEY``, and ``FOREIGN KEY`` constraints
* **SQL Generation**: Generate ``CREATE TABLE``, ``ALTER TABLE``, and ``DROP TABLE`` SQL statements
* **Schema Parsing**: Parse existing SQL schema strings back into Python objects
* **Type Safety**: Full type hints throughout the codebase
* **Integration Ready**: Seamlessly integrates with recordsQL for DML operations
* **Utility Functions**: Helper functions for type conversion, foreign key validation, and schema migrations

Quick Example
-------------

.. code-block:: python

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
   ]

   # Create table definition
   users_table = SQLTableInfo(name="users", columns=columns)

   # Generate CREATE TABLE SQL
   query, params = users_table.create_query()
   print(query)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
