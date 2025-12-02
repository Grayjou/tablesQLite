"""Tests for validation/names.py module."""

import pytest

from tablesqlite.validation.names import (
    KEYWORDS,
    is_number,
    standard_column_validation,
    standard_table_validation,
    validate_name,
)


class TestIsNumber:
    """Tests for is_number function."""

    def test_is_number_integer(self) -> None:
        """Test is_number with integer string."""
        assert is_number("123") is True
        assert is_number("-123") is True
        assert is_number("0") is True

    def test_is_number_float(self) -> None:
        """Test is_number with float string."""
        assert is_number("123.45") is True
        assert is_number("-123.45") is True
        assert is_number("0.0") is True

    def test_is_number_invalid(self) -> None:
        """Test is_number with non-number string."""
        assert is_number("abc") is False
        assert is_number("") is False
        assert is_number("12abc") is False
        assert is_number("abc12") is False


class TestValidateName:
    """Tests for validate_name function."""

    def test_validate_name_valid(self) -> None:
        """Test validate_name with valid names."""
        # Should not raise
        validate_name("users")
        validate_name("user_id")
        validate_name("UserName")
        validate_name("column123")
        validate_name("a")

    def test_validate_name_with_dot(self) -> None:
        """Test validate_name with dots allowed."""
        validate_name("table.column", allow_dot=True)
        validate_name("schema.table.column", allow_dot=True)

    def test_validate_name_with_dot_not_allowed(self) -> None:
        """Test validate_name with dots not allowed."""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_name("table.column", allow_dot=False)

    def test_validate_name_starts_with_digit(self) -> None:
        """Test validate_name with name starting with digit."""
        with pytest.raises(ValueError, match="cannot start with a digit"):
            validate_name("1column")

    def test_validate_name_empty(self) -> None:
        """Test validate_name with empty name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_name("")

    def test_validate_name_non_string(self) -> None:
        """Test validate_name with non-string."""
        with pytest.raises(TypeError, match="must be a string"):
            validate_name(123)  # type: ignore

    def test_validate_name_too_long(self) -> None:
        """Test validate_name with name too long."""
        with pytest.raises(ValueError, match="too long"):
            validate_name("a" * 256)

    def test_validate_name_max_len_custom(self) -> None:
        """Test validate_name with custom max_len."""
        validate_name("a" * 10, max_len=10)
        with pytest.raises(ValueError, match="too long"):
            validate_name("a" * 11, max_len=10)

    def test_validate_name_forbidden_chars(self) -> None:
        """Test validate_name with forbidden characters."""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_name("user@name")
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_name("user name")
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_name("user-name")

    def test_validate_name_reserved_words(self) -> None:
        """Test validate_name with reserved words."""
        for keyword in ["select", "from", "where", "table"]:
            with pytest.raises(ValueError, match="forbidden words"):
                validate_name(keyword)
            # Case insensitive
            with pytest.raises(ValueError, match="forbidden words"):
                validate_name(keyword.upper())

    def test_validate_name_skip_word_validation(self) -> None:
        """Test validate_name with word validation disabled."""
        # Should not raise
        validate_name("select", validate_words=False)
        validate_name("from", validate_words=False)

    def test_validate_name_skip_char_validation(self) -> None:
        """Test validate_name with char validation disabled."""
        # Should not raise
        validate_name("user-name", validate_chars=False)
        validate_name("user@name", validate_chars=False)

    def test_validate_name_allow_dollar(self) -> None:
        """Test validate_name with dollar sign allowed."""
        validate_name("$user", allow_dollar=True)
        validate_name("user$123", allow_dollar=True)

    def test_validate_name_forgiven_chars(self) -> None:
        """Test validate_name with forgiven characters."""
        validate_name("user-name", forgiven_chars={"-"})
        validate_name("user@name", forgiven_chars={"@"})

    def test_validate_name_consecutive_dots(self) -> None:
        """Test validate_name with consecutive dots."""
        with pytest.raises(ValueError, match="consecutive dots"):
            validate_name("table..column", allow_dot=True)

    def test_validate_name_leading_dot(self) -> None:
        """Test validate_name with leading dot."""
        with pytest.raises(ValueError, match="leading/trailing dot"):
            validate_name(".column", allow_dot=True)

    def test_validate_name_trailing_dot(self) -> None:
        """Test validate_name with trailing dot."""
        with pytest.raises(ValueError, match="leading/trailing dot"):
            validate_name("column.", allow_dot=True)

    def test_validate_name_dot_part_starts_with_digit(self) -> None:
        """Test validate_name with dot part starting with digit."""
        with pytest.raises(ValueError, match="not start with a digit"):
            validate_name("table.1column", allow_dot=True)

    def test_validate_name_number_not_allowed(self) -> None:
        """Test validate_name with number name not allowed."""
        with pytest.raises(ValueError, match="number not allowed"):
            validate_name("123")

    def test_validate_name_number_allowed(self) -> None:
        """Test validate_name with number name allowed."""
        validate_name("123", allow_number=True)
        validate_name("1column", allow_number=True)


class TestStandardColumnValidation:
    """Tests for standard_column_validation function."""

    def test_standard_column_validation_valid(self) -> None:
        """Test standard_column_validation with valid names."""
        standard_column_validation("column_name")
        standard_column_validation("id")
        standard_column_validation("user_id")

    def test_standard_column_validation_dot_not_allowed_by_default(self) -> None:
        """Test standard_column_validation with dot not allowed by default."""
        with pytest.raises(ValueError, match="forbidden characters"):
            standard_column_validation("table.column")


class TestStandardTableValidation:
    """Tests for standard_table_validation function."""

    def test_standard_table_validation_valid(self) -> None:
        """Test standard_table_validation with valid names."""
        standard_table_validation("users")
        standard_table_validation("user_orders")
        standard_table_validation("UserProfile")

    def test_standard_table_validation_dot_not_allowed_by_default(self) -> None:
        """Test standard_table_validation with dot not allowed by default."""
        with pytest.raises(ValueError, match="forbidden characters"):
            standard_table_validation("schema.table")


class TestKeywords:
    """Tests for KEYWORDS constant."""

    def test_keywords_contains_expected(self) -> None:
        """Test KEYWORDS contains expected SQL reserved words."""
        expected = {"select", "from", "where", "table", "insert", "update", "delete"}
        assert expected.issubset(KEYWORDS)

    def test_keywords_lowercase(self) -> None:
        """Test KEYWORDS are all lowercase."""
        for keyword in KEYWORDS:
            assert keyword == keyword.lower()
