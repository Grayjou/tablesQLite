# 📓 Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-05-12

### 🎉 Added

- Initial release of `recordsQL`, a SQL query builder built on top of `expressQL`
- Support for:
  - `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `WITH`
  - `INNER`, `LEFT`, `RIGHT`, and `FULL` joins
  - `COUNT`, `EXISTS`, and `ON CONFLICT` clauses
- Fluent, composable Pythonic API for building SQL queries
- Placeholder-based query parameterization for security
- CTE (Common Table Expression) chaining with `WITH` syntax
- Query modifiers like `ORDER_BY`, `LIMIT`, and `OFFSET`
- Utility types: `cols()`, `col()`, `text()`, and `num()`

## [0.1.1] - 2025-05-25
- Fixed a bug where integers couldn't be used as columns (e.g. SELECT 1 FROM ..., SELECT 3.14, ...)

## [0.1.2] - 2025-05-25
- Fixed a broken kwarg

### 🧪 Examples

- Demonstrative usage of `recordsQL` in `main.py`
- Output preview using `.placeholder_pair()` method for SQL + parameters

---

