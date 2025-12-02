"""Tests for validation/sql_datatypes.py module."""

import pytest

from tablesqlite.validation.sql_datatypes import (
    ALL_TYPES,
    PLACEHOLDER_INT_KEYS,
    Validator,
    bracket_tuple_from_str,
    get_validator,
    is_list_of_pairs,
    match_bracket_tuple,
    upper_before_bracket,
    validate_data_type,
)


class TestUpperBeforeBracket:
    """Tests for upper_before_bracket function."""

    def test_upper_before_bracket_no_bracket(self) -> None:
        """Test upper_before_bracket with no bracket."""
        assert upper_before_bracket("integer") == "INTEGER"
        assert upper_before_bracket("TEXT") == "TEXT"

    def test_upper_before_bracket_with_bracket(self) -> None:
        """Test upper_before_bracket with bracket."""
        assert upper_before_bracket("varchar(255)") == "VARCHAR(255)"
        assert upper_before_bracket("DECIMAL(10,2)") == "DECIMAL(10,2)"

    def test_upper_before_bracket_empty(self) -> None:
        """Test upper_before_bracket with empty string."""
        assert upper_before_bracket("") == ""


class TestBracketTupleFromStr:
    """Tests for bracket_tuple_from_str function."""

    def test_bracket_tuple_from_str_no_bracket(self) -> None:
        """Test bracket_tuple_from_str with no bracket."""
        type_, args = bracket_tuple_from_str("INTEGER")
        assert type_ == "INTEGER"
        assert args == ()

    def test_bracket_tuple_from_str_with_bracket(self) -> None:
        """Test bracket_tuple_from_str with bracket."""
        type_, args = bracket_tuple_from_str("VARCHAR(255)")
        assert type_ == "VARCHAR"
        assert args == ("255",)

    def test_bracket_tuple_from_str_multiple_args(self) -> None:
        """Test bracket_tuple_from_str with multiple args."""
        type_, args = bracket_tuple_from_str("DECIMAL(10, 2)")
        assert type_ == "DECIMAL"
        assert args == ("10", "2")

    def test_bracket_tuple_from_str_whitespace(self) -> None:
        """Test bracket_tuple_from_str with whitespace."""
        type_, args = bracket_tuple_from_str("  VARCHAR ( 100 ) ")
        assert type_.strip() == "VARCHAR"
        assert "100" in args[0]


class TestMatchBracketTuple:
    """Tests for match_bracket_tuple function."""

    def test_match_bracket_tuple_valid(self) -> None:
        """Test match_bracket_tuple with valid type."""
        pairs = {("INTEGER", ("size",)), ("VARCHAR", ("size",))}
        assert match_bracket_tuple("INTEGER", pairs) is True
        assert match_bracket_tuple("INTEGER(10)", pairs) is True
        assert match_bracket_tuple("VARCHAR(255)", pairs) is True

    def test_match_bracket_tuple_no_pairs(self) -> None:
        """Test match_bracket_tuple with no pairs."""
        assert match_bracket_tuple("INTEGER", None) is False
        assert match_bracket_tuple("INTEGER", set()) is False

    def test_match_bracket_tuple_wildcard(self) -> None:
        """Test match_bracket_tuple with wildcard."""
        pairs = {("ENUM", ("...",))}
        assert match_bracket_tuple("ENUM('a', 'b', 'c')", pairs) is True

    def test_match_bracket_tuple_too_many_args(self) -> None:
        """Test match_bracket_tuple with too many args."""
        pairs = {("INTEGER", ("size",))}
        assert match_bracket_tuple("INTEGER(10, 20)", pairs) is False


class TestIsListOfPairs:
    """Tests for is_list_of_pairs function."""

    def test_is_list_of_pairs_valid(self) -> None:
        """Test is_list_of_pairs with valid pairs."""
        assert is_list_of_pairs([("a", 1), ("b", 2)]) is True

    def test_is_list_of_pairs_invalid(self) -> None:
        """Test is_list_of_pairs with invalid pairs."""
        assert is_list_of_pairs([("a",)]) is False
        assert is_list_of_pairs([("a", 1, 2)]) is False
        assert is_list_of_pairs(["a"]) is False

    def test_is_list_of_pairs_empty(self) -> None:
        """Test is_list_of_pairs with empty list."""
        assert is_list_of_pairs([]) is True


class TestValidator:
    """Tests for Validator class."""

    def test_validator_init(self) -> None:
        """Test Validator initialization."""
        v = Validator()
        assert len(v) > 0

    def test_validator_validate_type_valid(self) -> None:
        """Test Validator.validate_type with valid types."""
        v = Validator()
        assert v.validate_type("INTEGER") is True
        assert v.validate_type("TEXT") is True
        assert v.validate_type("VARCHAR(255)") is True
        assert v.validate_type("DECIMAL(10)") is True

    def test_validator_validate_type_invalid(self) -> None:
        """Test Validator.validate_type with invalid types."""
        v = Validator()
        assert v.validate_type("INVALID_TYPE") is False

    def test_validator_add_type(self) -> None:
        """Test Validator.add_type."""
        v = Validator()
        v.add_type("CUSTOM_TYPE(size)")
        assert v.validate_type("CUSTOM_TYPE(10)") is True

    def test_validator_add_type_non_string(self) -> None:
        """Test Validator.add_type with non-string."""
        v = Validator()
        with pytest.raises(TypeError, match="must be a string"):
            v.add_type(123)  # type: ignore

    def test_validator_remove_type(self) -> None:
        """Test Validator.remove_type."""
        v = Validator()
        v.add_type("CUSTOM_TYPE")
        assert v.validate_type("CUSTOM_TYPE") is True
        v.remove_type("CUSTOM_TYPE")
        assert v.validate_type("CUSTOM_TYPE") is False

    def test_validator_remove_type_non_string(self) -> None:
        """Test Validator.remove_type with non-string."""
        v = Validator()
        with pytest.raises(TypeError, match="must be a string"):
            v.remove_type(123)  # type: ignore


class TestGetValidator:
    """Tests for get_validator function."""

    def test_get_validator_returns_validator(self) -> None:
        """Test get_validator returns a Validator instance."""
        v = get_validator()
        assert isinstance(v, Validator)

    def test_get_validator_singleton(self) -> None:
        """Test get_validator returns the same instance."""
        v1 = get_validator()
        v2 = get_validator()
        assert v1 is v2


class TestValidateDataType:
    """Tests for validate_data_type function."""

    def test_validate_data_type_valid(self) -> None:
        """Test validate_data_type with valid types."""
        assert validate_data_type("INTEGER") is True
        assert validate_data_type("TEXT") is True
        assert validate_data_type("BLOB") is True
        assert validate_data_type("REAL") is True
        assert validate_data_type("VARCHAR(255)") is True
        assert validate_data_type("DECIMAL(10)") is True

    def test_validate_data_type_case_insensitive(self) -> None:
        """Test validate_data_type is case insensitive."""
        assert validate_data_type("integer") is True
        assert validate_data_type("Integer") is True
        assert validate_data_type("varchar(100)") is True

    def test_validate_data_type_invalid(self) -> None:
        """Test validate_data_type with invalid type."""
        with pytest.raises(ValueError, match="Invalid data type"):
            validate_data_type("INVALID_TYPE")


class TestConstants:
    """Tests for module constants."""

    def test_all_types_not_empty(self) -> None:
        """Test ALL_TYPES is not empty."""
        assert len(ALL_TYPES) > 0

    def test_all_types_contains_common_types(self) -> None:
        """Test ALL_TYPES contains common SQL types."""
        type_names = [t.split("(")[0] for t in ALL_TYPES]
        assert "INTEGER" in type_names
        assert "TEXT" in type_names
        assert "BLOB" in type_names
        assert "VARCHAR" in type_names

    def test_placeholder_int_keys(self) -> None:
        """Test PLACEHOLDER_INT_KEYS contains expected values."""
        assert "size" in PLACEHOLDER_INT_KEYS
        assert "fsp" in PLACEHOLDER_INT_KEYS
        assert "p" in PLACEHOLDER_INT_KEYS
