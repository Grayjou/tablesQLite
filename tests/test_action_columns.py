"""Tests for action_queries/columns.py module."""

import pytest

from tablesqlite import SQLColumnInfo, SQLTableInfo
from tablesqlite.action_queries.columns import (
    _extract_table_name,
    add_column_query,
    drop_column_query,
    rename_column_query,
)


class TestExtractTableName:
    """Tests for _extract_table_name function."""

    def test_extract_table_name_from_string(self) -> None:
        """Test _extract_table_name with string."""
        assert _extract_table_name("users") == "users"

    def test_extract_table_name_from_quoted_string(self) -> None:
        """Test _extract_table_name with quoted string."""
        assert _extract_table_name('"users"') == "users"
        assert _extract_table_name("'users'") == "users"

    def test_extract_table_name_from_table_info(self) -> None:
        """Test _extract_table_name with SQLTableInfo."""
        table = SQLTableInfo("users")
        assert _extract_table_name(table) == "users"

    def test_extract_table_name_invalid_type(self) -> None:
        """Test _extract_table_name with invalid type."""
        with pytest.raises(TypeError, match="must be a string"):
            _extract_table_name(123)

    def test_extract_table_name_with_check_callback(self) -> None:
        """Test _extract_table_name with check callback."""
        check_called = [False]

        def check(table_obj):
            check_called[0] = True

        table = SQLTableInfo("users")
        _extract_table_name(table, check)
        assert check_called[0] is True


class TestAddColumnQuery:
    """Tests for add_column_query function."""

    def test_add_column_query_basic(self) -> None:
        """Test add_column_query with basic column."""
        col = SQLColumnInfo("email", "TEXT")
        query, params = add_column_query("users", col)
        assert "ALTER TABLE" in query
        assert '"users"' in query
        assert "ADD COLUMN" in query
        assert '"email"' in query
        assert "TEXT" in query
        assert params == []

    def test_add_column_query_with_constraints(self) -> None:
        """Test add_column_query with column constraints."""
        col = SQLColumnInfo("email", "TEXT", not_null=True, unique=True)
        query, params = add_column_query("users", col)
        assert "NOT NULL" in query
        assert "UNIQUE" in query

    def test_add_column_query_with_table_info(self) -> None:
        """Test add_column_query with SQLTableInfo."""
        table = SQLTableInfo("users")
        col = SQLColumnInfo("email", "TEXT")
        query, params = add_column_query(table, col)
        assert '"users"' in query

    def test_add_column_query_invalid_column_type(self) -> None:
        """Test add_column_query with invalid column type."""
        with pytest.raises(TypeError, match="must be an instance"):
            add_column_query("users", "not a column")

    def test_add_column_query_check_if_possible(self) -> None:
        """Test add_column_query with check_if_possible."""
        col1 = SQLColumnInfo("id", "INTEGER")
        col2 = SQLColumnInfo("id", "TEXT")  # Same name
        table = SQLTableInfo("users", columns=[col1])
        with pytest.raises(ValueError, match="already exists"):
            add_column_query(table, col2, check_if_possible=True)


class TestDropColumnQuery:
    """Tests for drop_column_query function."""

    def test_drop_column_query_basic(self) -> None:
        """Test drop_column_query with basic column name."""
        query, params = drop_column_query("users", "email")
        assert "ALTER TABLE" in query
        assert '"users"' in query
        assert "DROP COLUMN" in query
        assert '"email"' in query
        assert params == []

    def test_drop_column_query_with_table_info(self) -> None:
        """Test drop_column_query with SQLTableInfo."""
        table = SQLTableInfo("users")
        query, params = drop_column_query(table, "email")
        assert '"users"' in query

    def test_drop_column_query_check_if_possible_exists(self) -> None:
        """Test drop_column_query with check_if_possible and column exists."""
        col = SQLColumnInfo("email", "TEXT")
        table = SQLTableInfo("users", columns=[col])
        query, params = drop_column_query(table, "email", check_if_possible=True)
        assert "DROP COLUMN" in query

    def test_drop_column_query_check_if_possible_not_exists(self) -> None:
        """Test drop_column_query with check_if_possible and column doesn't exist."""
        table = SQLTableInfo("users")
        with pytest.raises(ValueError, match="does not exist"):
            drop_column_query(table, "email", check_if_possible=True)


class TestRenameColumnQuery:
    """Tests for rename_column_query function."""

    def test_rename_column_query_basic(self) -> None:
        """Test rename_column_query with basic names."""
        query, params = rename_column_query("users", "email", "user_email")
        assert "ALTER TABLE" in query
        assert '"users"' in query
        assert "RENAME COLUMN" in query
        assert '"email"' in query
        assert '"user_email"' in query
        assert params == []

    def test_rename_column_query_with_table_info(self) -> None:
        """Test rename_column_query with SQLTableInfo."""
        table = SQLTableInfo("users")
        query, params = rename_column_query(table, "email", "user_email")
        assert '"users"' in query

    def test_rename_column_query_check_if_possible_old_not_exists(self) -> None:
        """Test rename_column_query when old column doesn't exist."""
        table = SQLTableInfo("users")
        with pytest.raises(ValueError, match="does not exist"):
            rename_column_query(table, "email", "user_email", check_if_possible=True)

    def test_rename_column_query_check_if_possible_new_exists(self) -> None:
        """Test rename_column_query when new column name already exists."""
        col1 = SQLColumnInfo("email", "TEXT")
        col2 = SQLColumnInfo("user_email", "TEXT")
        table = SQLTableInfo("users", columns=[col1, col2])
        with pytest.raises(ValueError, match="already exists"):
            rename_column_query(table, "email", "user_email", check_if_possible=True)

    def test_rename_column_query_check_if_possible_valid(self) -> None:
        """Test rename_column_query with valid rename."""
        col = SQLColumnInfo("email", "TEXT")
        table = SQLTableInfo("users", columns=[col])
        query, params = rename_column_query(
            table, "email", "user_email", check_if_possible=True
        )
        assert "RENAME COLUMN" in query
