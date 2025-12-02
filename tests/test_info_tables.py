"""Tests for info_queries/tables.py module."""

import pytest

from tablesqlite.info_queries.tables import (
    count_rows_query,
    get_all_tables_query,
    get_table_info_query,
)


class TestGetAllTablesQuery:
    """Tests for get_all_tables_query function."""

    def test_get_all_tables_query(self) -> None:
        """Test get_all_tables_query returns correct query."""
        query, params = get_all_tables_query()
        assert query == "SELECT name FROM sqlite_master WHERE type='table'"
        assert params == []


class TestGetTableInfoQuery:
    """Tests for get_table_info_query function."""

    def test_get_table_info_query_basic(self) -> None:
        """Test get_table_info_query with basic table name."""
        query, params = get_table_info_query("users")
        assert query == "PRAGMA table_info('users')"
        assert params == []

    def test_get_table_info_query_invalid_name(self) -> None:
        """Table names are validated when not pre-validated."""
        with pytest.raises(ValueError):
            get_table_info_query("invalid.name")

    def test_get_table_info_query_already_validated(self) -> None:
        """Test get_table_info_query with already_validated flag."""
        query, params = get_table_info_query("invalid.name", already_validated=True)
        assert query == "PRAGMA table_info('invalid.name')"


class TestCountRowsQuery:
    """Tests for count_rows_query function."""

    def test_count_rows_query_basic(self) -> None:
        """Test count_rows_query with basic table name."""
        query, params = count_rows_query("users")
        assert query == "SELECT COUNT(*) FROM 'users'"
        assert params == []

    def test_count_rows_query_invalid_name(self) -> None:
        """Table names are validated for count_rows_query."""
        with pytest.raises(ValueError):
            count_rows_query("invalid.table")

    def test_count_rows_query_already_validated(self) -> None:
        """Test count_rows_query with already_validated flag."""
        query, params = count_rows_query("invalid.table", already_validated=True)
        assert query == "SELECT COUNT(*) FROM 'invalid.table'"


class TestValidateTableNameDecorator:
    """Tests for validate_table_name decorator."""

    def test_validate_table_name_decorator_valid(self) -> None:
        """Test decorator with valid table name."""
        query, params = get_table_info_query("valid_table")
        assert "valid_table" in query

    def test_validate_table_name_decorator_invalid(self) -> None:
        """Test decorator with invalid table name."""
        with pytest.raises(ValueError):
            get_table_info_query("invalid.table")
