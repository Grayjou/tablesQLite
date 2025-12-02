"""Tests for action_queries/tables.py module."""

import pytest

from tablesqlite import SQLColumnInfo, SQLTableInfo
from tablesqlite.action_queries.tables import (
    _extract_table_name,
    create_table_query,
    drop_table_query,
    rename_table_query,
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


class TestCreateTableQuery:
    """Tests for create_table_query function."""

    def test_create_table_query_basic(self) -> None:
        """Test create_table_query with basic table."""
        cols = [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT"),
        ]
        table = SQLTableInfo("users", columns=cols)
        query, params = create_table_query(table)
        assert "CREATE TABLE" in query
        assert '"users"' in query
        assert '"id"' in query
        assert '"name"' in query
        assert params == []

    def test_create_table_query_with_constraints(self) -> None:
        """Test create_table_query with column constraints."""
        cols = [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("email", "TEXT", not_null=True, unique=True),
        ]
        table = SQLTableInfo("users", columns=cols)
        query, params = create_table_query(table)
        assert "PRIMARY KEY" in query
        assert "NOT NULL" in query
        assert "UNIQUE" in query

    def test_create_table_query_with_foreign_key(self) -> None:
        """Test create_table_query with foreign key."""
        cols = [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo(
                "user_id", "INTEGER", foreign_key={"table": "users", "column": "id"}
            ),
        ]
        table = SQLTableInfo("posts", columns=cols)
        query, params = create_table_query(table)
        assert "FOREIGN KEY" in query
        assert "REFERENCES users" in query

    def test_create_table_query_empty_table(self) -> None:
        """Test create_table_query with empty table."""
        table = SQLTableInfo("empty")
        query, params = create_table_query(table)
        assert "CREATE TABLE" in query
        assert '"empty"' in query


class TestDropTableQuery:
    """Tests for drop_table_query function."""

    def test_drop_table_query_basic(self) -> None:
        """Test drop_table_query with basic table name."""
        query, params = drop_table_query("users")
        assert query == "DROP TABLE users"
        assert params == []

    def test_drop_table_query_with_table_info(self) -> None:
        """Test drop_table_query with SQLTableInfo."""
        table = SQLTableInfo("users")
        query, params = drop_table_query(table)
        assert query == "DROP TABLE users"

    def test_drop_table_query_if_exists(self) -> None:
        """Test drop_table_query with check_if_exists."""
        query, params = drop_table_query("users", check_if_exists=True)
        assert query == "DROP TABLE IF EXISTS users"

    def test_drop_table_query_quoted_name(self) -> None:
        """Test drop_table_query strips quotes."""
        query, params = drop_table_query('"users"')
        assert query == "DROP TABLE users"


class TestRenameTableQuery:
    """Tests for rename_table_query function."""

    def test_rename_table_query_basic(self) -> None:
        """Test rename_table_query with basic names."""
        query, params = rename_table_query("users", "customers")
        assert query == "ALTER TABLE users RENAME TO customers"
        assert params == []

    def test_rename_table_query_if_exists(self) -> None:
        """Test rename_table_query with check_if_exists."""
        query, params = rename_table_query("users", "customers", check_if_exists=True)
        assert query == "ALTER TABLE IF EXISTS users RENAME TO customers"
