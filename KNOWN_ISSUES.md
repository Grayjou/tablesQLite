# Known Issues

This document tracks known issues discovered during testing of the `tablesqlite` package.

## Issues in tablesqlite

### 1. Empty name validation causes IndexError

**Location:** `tablesqlite/validation/names.py` - `validate_name()` function

**Description:** The function checks `name[0].isdigit()` before checking if the name is empty, causing an `IndexError` when an empty string is passed.

**Current behavior:**
```python
validate_name("")  # Raises IndexError: string index out of range
```

**Expected behavior:** Should raise `ValueError` with message "Column name cannot be empty."

**Suggested fix:** Move the empty string check before the digit check:
```python
if len(name) == 0:
    raise ValueError("Column name cannot be empty.")
if name[0].isdigit() and not allow_number:
    raise ValueError("Column name cannot start with a digit.")
```

---

### 2. `allow_number` flag doesn't work correctly

**Location:** `tablesqlite/validation/names.py` - `validate_name()` function

**Description:** When `allow_number=True`, the function still raises an error for names starting with digits because the digit check doesn't use the `allow_number` flag.

**Current behavior:**
```python
validate_name("123", allow_number=True)  # Raises ValueError: Name cannot start with a digit.
```

**Expected behavior:** Should allow numeric names when `allow_number=True`.

**Note:** Looking at the code, the issue is that the number check uses `is_number(name)` but the `allow_number` parameter isn't connected to the digit-start check. The `allow_number` parameter appears to be for allowing pure numeric column names but there's `allow_digit` in the expressql version.

---

### 3. Composite Primary Key with INTEGER columns raises incorrect error

**Location:** `tablesqlite/objects/info_objects.py` - `_validate_auto_increment()` method

**Description:** When creating a table with composite primary keys where both columns are INTEGER type, the system incorrectly raises "Only one column can be auto increment" error.

**Current behavior:**
```python
cols = [
    SQLColumnInfoBase("user_id", "INTEGER", primary_key=True),
    SQLColumnInfoBase("post_id", "INTEGER", primary_key=True),
]
table = SQLTableInfoBase("likes", columns=cols)
# Raises ValueError: Only one column can be auto increment
```

**Expected behavior:** Composite primary keys with INTEGER columns should work correctly. Auto-increment only applies to single INTEGER PRIMARY KEY columns, not composite keys.

**Root cause:** The `auto_increment` property returns `True` for any `INTEGER PRIMARY KEY` column, without considering whether it's part of a composite primary key.

**Suggested fix:** The `auto_increment` property should consider whether there's only one primary key column in the table, or the validation should account for this case.

---

### 4. `validate_table_name` decorator fails with optional arguments

**Location:** `tablesqlite/info_queries/tables.py` - `validate_table_name()` decorator

**Description:** The decorator tries to access `args[1]` (the `already_validated` argument) directly, but when the optional argument is not provided, `args` only has one element, causing an `IndexError`.

**Current behavior:**
```python
get_table_info_query("users")  # Raises IndexError: tuple index out of range
```

**Expected behavior:** Should work correctly when optional arguments are omitted.

**Suggested fix:** The decorator should check `len(args)` before accessing `args[already_validated_pos]` or use `kwargs.get()` to handle optional arguments:
```python
if already_validated_pos is not None and len(args) > already_validated_pos:
    already_validated = args[already_validated_pos]
else:
    already_validated = kwargs.get('already_validated', False)
```

---

### 5. `validate_table_name` decorator has inverted logic

**Location:** `tablesqlite/info_queries/tables.py` - `validate_table_name()` decorator

**Description:** The decorator validates the table name when `already_validated=True`, but it should skip validation when the name is already validated.

**Current behavior:**
```python
# Validates when already_validated=True (incorrect)
if validate:  # validate == already_validated
    validate_name(table_name, allow_dot=False)
```

**Expected behavior:** Should skip validation when `already_validated=True`.

**Suggested fix:**
```python
if not already_validated:  # Skip validation if already validated
    validate_name(table_name, allow_dot=False)
```

---

## Issues in expressQL (External Dependency)

### 1. Cannot parse complex CHECK constraints with IN expressions

**Description:** The `parse_condition()` function from expressQL cannot handle CHECK constraints that use IN expressions with quoted string values.

**Example that fails:**
```python
from expressql import parse_condition
parse_condition("status IN ('pending', 'completed', 'cancelled')")
# Raises ValueError: Column name contains forbidden characters
```

This affects `tablesqlite`'s ability to parse complex SQL schemas with CHECK constraints.

---

### 2. SQL literal "NULL" causes validation issues

**Description:** When using "NULL" as a default value, the expressQL validator may reject it as a forbidden word.

**Example:**
```python
from expressql import col
col("NULL")  # May cause validation issues
```

This affects `tablesqlite`'s handling of NULL default values.

---

## Test Coverage Summary

| Module | Tests | Passed | Skipped | Failed |
|--------|-------|--------|---------|--------|
| test_generic.py | 22 | 22 | 0 | 0 |
| test_custom_types.py | 11 | 11 | 0 | 0 |
| test_names.py | 21 | 19 | 0 | 2* |
| test_path.py | 18 | 18 | 0 | 0 |
| test_sql_datatypes.py | 23 | 23 | 0 | 0 |
| test_enforcers.py | 16 | 16 | 0 | 0 |
| test_info_objects.py | 58 | 52 | 4 | 2* |
| test_action_columns.py | 14 | 14 | 0 | 0 |
| test_action_tables.py | 10 | 10 | 0 | 0 |
| test_schema_parse.py | 20 | 18 | 2 | 0 |
| test_info_tables.py | 6 | 4 | 2 | 0 |
| test_query_wrappers.py | 40 | 39 | 1 | 0 |

*Tests marked as expected failures that document bugs rather than test failures.

## Recommendations

1. **High Priority:** Fix the empty name validation bug - it's a common edge case that will affect users.

2. **High Priority:** Fix the composite primary key issue - this is a significant limitation for users who need composite keys.

3. **Medium Priority:** Fix the decorator issues in `validate_table_name` - the inverted logic and missing optional argument handling make the API confusing.

4. **Low Priority:** Consider reporting the expressQL issues upstream or adding workarounds for complex CHECK constraints.
