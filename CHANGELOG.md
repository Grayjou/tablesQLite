# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.7] - 2025-12-02

### Fixed

- Adjusted column and table name validation to raise empty-name errors before character access, respect `allow_number` for numeric identifiers, and honor the `already_validated` flag when decorating table queries.
- Limited auto-increment detection to single-column INTEGER primary keys to prevent false conflicts for composite keys.
- Corrected `ALTER TABLE IF EXISTS` rename SQL formatting and documented current expressQL 0.3.7 behaviors in `KNOWN_ISSUES.md`.

## [0.1.0] - 2025-05-28

### Added

- Initial release of `tablesQLite` 🎉
- Define tables declaratively using `SQLTableInfo` and `SQLColumnInfo`.
- Support for advanced constraints: `NOT NULL`, `DEFAULT`, `CHECK`, `UNIQUE`, `PRIMARY KEY`, and `FOREIGN KEY`.
- Table-level methods for:
  - Creating SQL `CREATE TABLE` statements.
  - Parsing SQL table schema from a query string.
  - Serializing/deserializing table definitions with `.to_dict()` and `.from_sql_schema()`.
- Integration-ready design:
  - Seamlessly integrates with [`recordsQL`](https://pypi.org/project/recordsQL) for insert, update, select, delete, etc.
  - Optional `add_query_methods()` patch to inject record query methods directly into `SQLTableInfo`.

### Notes

- This version is a developer-focused initial release, aimed at enabling full control over SQLite schema generation and manipulation.
- Focuses on SQLite DDL (schema logic); DML logic is offloaded to `recordsQL`.
