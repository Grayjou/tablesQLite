# Known Issues

This document tracks current and recently resolved issues for the `tablesqlite` package.

## Issues in tablesqlite

### 1. Name validation edge cases (resolved)
- `validate_name` now raises `ValueError("Column name cannot be empty.")` before any character access.
- Digit-prefixed and fully numeric identifiers are allowed when `allow_number=True`, while still being rejected otherwise.

### 2. Composite INTEGER primary keys (resolved)
- `_validate_auto_increment` only treats an `INTEGER PRIMARY KEY` as auto-increment when it is the sole primary key column, preventing conflicts for composite keys.

### 3. `validate_table_name` decorator arguments (resolved)
- The decorator now safely handles omitted optional arguments and respects `already_validated=False` as the condition to trigger validation, preventing `IndexError` and double validation.

### 4. `rename_table_query` IF EXISTS placement (resolved)
- The function now formats SQL as `ALTER TABLE IF EXISTS <old> RENAME TO <new>` when `check_if_exists=True`.

## Issues in expressQL (External Dependency)

### 1. Quoted IN checks (resolved upstream)
- expressQL 0.3.7 accepts `parse_condition("status IN ('pending', 'completed', 'cancelled')")` and similar quoted `IN` expressions.
- No additional workarounds are required in `tablesqlite` for these checks.

### 2. `col("NULL")` default handling (open)
- expressQL 0.3.7 still raises `ValueError("Name contains forbidden words: null")` when calling `col("NULL")`.
- Workaround: use Python `None` for NULL defaults in `tablesqlite` APIs so built-in default handling emits the proper SQL literal instead of constructing `col("NULL")` manually.
