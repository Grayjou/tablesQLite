"""Tests for validation/enforcers.py module."""

import pytest

from tablesqlite.objects.generic import Unknown
from tablesqlite.validation.enforcers import (
    BoolContainer,
    DualContainer,
    UndeterminedContainer,
    add_bool_properties,
    add_undetermined_properties,
    keys_exist_in_dict,
)


class TestKeysExistInDict:
    """Tests for keys_exist_in_dict function."""

    def test_keys_exist_in_dict_all_exist(self) -> None:
        """Test keys_exist_in_dict with all keys existing."""
        d = {"a": 1, "b": 2, "c": 3}
        assert keys_exist_in_dict(d, ["a", "b"]) is True
        assert keys_exist_in_dict(d, ["a", "b", "c"]) is True

    def test_keys_exist_in_dict_some_missing(self) -> None:
        """Test keys_exist_in_dict with some keys missing."""
        d = {"a": 1, "b": 2}
        assert keys_exist_in_dict(d, ["a", "c"]) is False
        assert keys_exist_in_dict(d, ["d"]) is False

    def test_keys_exist_in_dict_empty_keys(self) -> None:
        """Test keys_exist_in_dict with empty keys list."""
        d = {"a": 1}
        assert keys_exist_in_dict(d, []) is True

    def test_keys_exist_in_dict_empty_dict(self) -> None:
        """Test keys_exist_in_dict with empty dict."""
        assert keys_exist_in_dict({}, []) is True
        assert keys_exist_in_dict({}, ["a"]) is False


class TestAddBoolProperties:
    """Tests for add_bool_properties decorator."""

    def test_add_bool_properties_basic(self) -> None:
        """Test add_bool_properties adds properties."""

        @add_bool_properties("enabled", "active")
        class TestClass(BoolContainer):
            pass

        obj = TestClass()
        obj.enabled = True
        obj.active = False
        assert obj.enabled is True
        assert obj.active is False

    def test_add_bool_properties_validation(self) -> None:
        """Test add_bool_properties validates values."""

        @add_bool_properties("enabled")
        class TestClass(BoolContainer):
            pass

        obj = TestClass()
        obj.enabled = True
        assert obj.enabled is True

        with pytest.raises(ValueError):
            obj.enabled = "invalid"


class TestAddUndeterminedProperties:
    """Tests for add_undetermined_properties decorator."""

    def test_add_undetermined_properties_basic(self) -> None:
        """Test add_undetermined_properties adds properties."""

        @add_undetermined_properties(value=int)
        class TestClass(UndeterminedContainer):
            pass

        obj = TestClass()
        obj.value = 42
        assert obj.value == 42

    def test_add_undetermined_properties_accepts_unknown(self) -> None:
        """Test add_undetermined_properties accepts Unknown."""

        @add_undetermined_properties(value=int)
        class TestClass(UndeterminedContainer):
            pass

        obj = TestClass()
        unknown_val = Unknown("test")
        obj.value = unknown_val
        assert obj.value == unknown_val

    def test_add_undetermined_properties_validation(self) -> None:
        """Test add_undetermined_properties validates values."""

        @add_undetermined_properties(value=int)
        class TestClass(UndeterminedContainer):
            pass

        obj = TestClass()
        with pytest.raises(ValueError, match="Invalid value"):
            obj.value = "not an int"


class TestBoolContainer:
    """Tests for BoolContainer class."""

    def test_set_bool_attr_valid(self) -> None:
        """Test _set_bool_attr with valid values."""
        container = BoolContainer()
        container._set_bool_attr("_enabled", True)
        assert container._enabled is True

        container._set_bool_attr("_enabled", False)
        assert container._enabled is False

    def test_set_bool_attr_invalid(self) -> None:
        """Test _set_bool_attr with invalid values."""
        container = BoolContainer()
        with pytest.raises(ValueError):
            container._set_bool_attr("_enabled", "not a bool")


class TestUndeterminedContainer:
    """Tests for UndeterminedContainer class."""

    def test_set_undetermined_attr_valid_type(self) -> None:
        """Test _set_undetermined_attr with valid type."""
        container = UndeterminedContainer()
        container._set_undetermined_attr("_value", 42, int)
        assert container._value == 42

    def test_set_undetermined_attr_unknown(self) -> None:
        """Test _set_undetermined_attr with Unknown."""
        container = UndeterminedContainer()
        unknown_val = Unknown("test")
        container._set_undetermined_attr("_value", unknown_val, int)
        assert container._value == unknown_val

    def test_set_undetermined_attr_none(self) -> None:
        """Test _set_undetermined_attr with None."""
        container = UndeterminedContainer()
        container._set_undetermined_attr("_value", None, int)
        assert container._value is None

    def test_set_undetermined_attr_invalid_type(self) -> None:
        """Test _set_undetermined_attr with invalid type."""
        container = UndeterminedContainer()
        with pytest.raises(ValueError, match="Invalid value"):
            container._set_undetermined_attr("_value", "not an int", int)


class TestDualContainer:
    """Tests for DualContainer class."""

    def test_dual_container_inherits_from_both(self) -> None:
        """Test DualContainer inherits from both base classes."""
        container = DualContainer()
        assert isinstance(container, BoolContainer)
        assert isinstance(container, UndeterminedContainer)

    def test_dual_container_set_bool(self) -> None:
        """Test DualContainer _set_bool_attr method."""
        container = DualContainer()
        container._set_bool_attr("_enabled", True)
        assert container._enabled is True

    def test_dual_container_set_undetermined(self) -> None:
        """Test DualContainer _set_undetermined_attr method."""
        container = DualContainer()
        container._set_undetermined_attr("_value", 42, int)
        assert container._value == 42
