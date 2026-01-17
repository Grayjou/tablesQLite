"""Property enforcement utilities.

This module provides decorators and base classes for enforcing
property types and validation in data classes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union, get_args, get_origin

from ..objects.generic import is_undetermined
from .custom_types import ensure_all_bools


def _is_instance_of_type(value: Any, accepted_type: type) -> bool:
    """Check if a value is an instance of the accepted type, handling Union types.

    In Python 3.9, Union types cannot be used directly with isinstance(),
    so we need to handle them specially.

    Args:
        value: The value to check.
        accepted_type: The type to check against.

    Returns:
        True if the value is an instance of the accepted type.
    """
    # Handle Union types specially for Python 3.9 compatibility
    if get_origin(accepted_type) is Union:
        return any(isinstance(value, arg) for arg in get_args(accepted_type))
    else:
        return isinstance(value, accepted_type)


def keys_exist_in_dict(d: dict[str, Any], keys: list[str]) -> bool:
    """Check if all keys exist in a dictionary.

    Args:
        d: The dictionary to check.
        keys: List of keys to check for.

    Returns:
        True if all keys exist in the dictionary.
    """
    return all(key in d for key in keys)


def add_bool_properties(*attrs: str) -> Callable[[type], type]:
    """Class decorator that dynamically adds boolean properties.

    Adds properties with automatic validation for boolean values.

    Args:
        *attrs: Names of attributes to add as boolean properties.

    Returns:
        A class decorator function.
    """

    def wrapper(cls: type) -> type:
        for attr in attrs:
            private_attr = "_" + attr

            def getter(self: BoolContainer, attr: str = private_attr) -> bool:
                return getattr(self, attr)

            def setter(
                self: BoolContainer, value: Any, attr_name: str = private_attr
            ) -> None:
                self._set_bool_attr(attr_name, value)

            setattr(cls, attr, property(getter, setter))
        return cls

    return wrapper


def add_undetermined_properties(**typed_attrs: type) -> Callable[[type], type]:
    """Class decorator that dynamically adds typed or Unknown properties.

    Adds properties which must be either of a specified type or an
    'Unknown' object (checked via is_undetermined).

    Args:
        **typed_attrs: Mapping of attribute names to their accepted types.

    Returns:
        A class decorator function.
    """

    def wrapper(cls: type) -> type:
        for attr_name, accepted_type in typed_attrs.items():
            private_attr = "_" + attr_name

            def getter(self: UndeterminedContainer, attr: str = private_attr) -> Any:
                return getattr(self, attr)

            def setter(
                self: UndeterminedContainer,
                value: Any,
                attr_name: str = private_attr,
                accepted_type: type = accepted_type,
            ) -> None:
                self._set_undetermined_attr(attr_name, value, accepted_type)

            setattr(cls, attr_name, property(getter, setter))
        return cls

    return wrapper


class BoolContainer:
    """Base class for objects with boolean properties.

    Provides validation for boolean property setters.
    """

    def _set_bool_attr(self, attr_name: str, value: Any) -> None:
        """Set a boolean attribute with validation.

        Args:
            attr_name: The name of the attribute to set.
            value: The value to set.

        Raises:
            ValueError: If the value is not a valid boolean.
        """
        ensure_all_bools([value], return_false_on_error=False)
        setattr(self, attr_name, value)


class UndeterminedContainer:
    """Base class for objects with typed or Unknown properties.

    Provides validation for properties that can be either a specific
    type or an 'Unknown' object.
    """

    def _set_undetermined_attr(
        self, attr_name: str, value: Any, accepted_type: type
    ) -> None:
        """Set an attribute that can be typed or Unknown.

        Args:
            attr_name: The name of the attribute to set.
            value: The value to set.
            accepted_type: The accepted type for the value.

        Raises:
            ValueError: If the value is not of the accepted type or Unknown.
        """
        if not is_undetermined(value) and not _is_instance_of_type(
            value, accepted_type
        ):
            raise ValueError(
                f"Invalid value for '{attr_name}': {value} "
                f"(must be {accepted_type.__name__} or Unknown)"
            )
        setattr(self, attr_name, value)


class DualContainer(BoolContainer, UndeterminedContainer):
    """Base class combining BoolContainer and UndeterminedContainer.

    Allows for attributes that can be either boolean or of a specific type,
    or an 'Unknown' object.
    """

    def _set_bool_attr(self, attr_name: str, value: Any) -> None:
        """Set a boolean attribute with validation.

        Args:
            attr_name: The name of the attribute to set.
            value: The value to set.
        """
        super()._set_bool_attr(attr_name, value)

    def _set_undetermined_attr(
        self, attr_name: str, value: Any, accepted_type: type
    ) -> None:
        """Set an attribute that can be typed or Unknown.

        Args:
            attr_name: The name of the attribute to set.
            value: The value to set.
            accepted_type: The accepted type for the value.
        """
        super()._set_undetermined_attr(attr_name, value, accepted_type)

