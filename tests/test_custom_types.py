"""Tests for validation/custom_types.py module."""

import pytest

from tablesqlite.validation.custom_types import ensure_all_bools, ensure_bool


class TestEnsureBool:
    """Tests for ensure_bool function."""

    def test_ensure_bool_true(self) -> None:
        """Test ensure_bool with True."""
        assert ensure_bool(True) is True

    def test_ensure_bool_false(self) -> None:
        """Test ensure_bool with False."""
        assert ensure_bool(False) is False

    def test_ensure_bool_string_true(self) -> None:
        """Test ensure_bool with string 'true'."""
        assert ensure_bool("true") is True
        assert ensure_bool("True") is True
        assert ensure_bool("TRUE") is True
        assert ensure_bool("1") is True

    def test_ensure_bool_string_false(self) -> None:
        """Test ensure_bool with string 'false'."""
        assert ensure_bool("false") is False
        assert ensure_bool("False") is False
        assert ensure_bool("FALSE") is False
        assert ensure_bool("0") is False

    def test_ensure_bool_int_true(self) -> None:
        """Test ensure_bool with int 1."""
        assert ensure_bool(1) is True

    def test_ensure_bool_int_false(self) -> None:
        """Test ensure_bool with int 0."""
        assert ensure_bool(0) is False

    def test_ensure_bool_invalid_raises(self) -> None:
        """Test ensure_bool with invalid value raises ValueError."""
        with pytest.raises(ValueError, match="Expected a boolean value"):
            ensure_bool("invalid")
        with pytest.raises(ValueError, match="Expected a boolean value"):
            ensure_bool(2)
        with pytest.raises(ValueError, match="Expected a boolean value"):
            ensure_bool(-1)

    def test_ensure_bool_return_false_on_error(self) -> None:
        """Test ensure_bool with return_false_on_error=True."""
        assert ensure_bool("invalid", return_false_on_error=True) is False
        assert ensure_bool(2, return_false_on_error=True) is False
        assert ensure_bool(-1, return_false_on_error=True) is False


class TestEnsureAllBools:
    """Tests for ensure_all_bools function."""

    def test_ensure_all_bools_valid(self) -> None:
        """Test ensure_all_bools with valid values."""
        result = ensure_all_bools([True, False, "true", "false", 1, 0])
        assert result == [True, False, True, False, True, False]

    def test_ensure_all_bools_empty(self) -> None:
        """Test ensure_all_bools with empty list."""
        assert ensure_all_bools([]) == []

    def test_ensure_all_bools_invalid_raises(self) -> None:
        """Test ensure_all_bools with invalid value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid boolean value in list"):
            ensure_all_bools([True, "invalid", False])

    def test_ensure_all_bools_return_false_on_error(self) -> None:
        """Test ensure_all_bools with return_false_on_error=True."""
        result = ensure_all_bools(
            [True, "invalid", False], return_false_on_error=True
        )
        assert result == [True, False, False]

    def test_ensure_all_bools_generator(self) -> None:
        """Test ensure_all_bools with generator input."""
        gen = (x for x in [True, False, True])
        result = ensure_all_bools(gen)
        assert result == [True, False, True]
