Installation
============

Requirements
------------

* Python 3.10 or higher
* pip

Using pip
---------

Install tablesQLite from PyPI:

.. code-block:: bash

   pip install tablesqlite

Development Installation
------------------------

To install tablesQLite with development dependencies:

.. code-block:: bash

   pip install tablesqlite[dev]

This installs:

* pytest - for running tests
* mypy - for type checking
* ruff - for linting

Documentation Dependencies
--------------------------

To build the documentation locally:

.. code-block:: bash

   pip install tablesqlite[docs]

This installs Sphinx and related documentation tools.

From Source
-----------

To install from source:

.. code-block:: bash

   git clone https://github.com/Grayjou/tablesqlite.git
   cd tablesqlite
   pip install -e .

For development:

.. code-block:: bash

   pip install -e .[dev]

Dependencies
------------

tablesQLite has the following runtime dependencies:

* **expressQL** (>=0.3.6) - SQL expression builder
* **sortedcontainers** (>=2.4.0) - Sorted container types

These dependencies are automatically installed when you install tablesQLite.

Verifying Installation
----------------------

To verify that tablesQLite is installed correctly:

.. code-block:: python

   import tablesqlite
   print(tablesqlite.__version__)

You should see the version number printed (e.g., ``0.1.7``).
