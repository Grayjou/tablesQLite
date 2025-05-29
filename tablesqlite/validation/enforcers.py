from __future__ import annotations
from .custom_types import ensure_all_bools
from ..objects.generic import is_undetermined



def keys_exist_in_dict(d, keys):
    return all(key in d for key in keys)


def add_bool_properties(*attrs: str):
    """
    Class decorator that dynamically adds boolean properties
    with automatic validation.
    """
    def wrapper(cls):
        for attr in attrs:
            private_attr = "_" + attr

            def getter(self:BoolContainer, attr=private_attr) -> bool:
                return getattr(self, attr)

            def setter(self:BoolContainer, value, attr_name=private_attr) -> None:
                self._set_bool_attr(attr_name, value)

            setattr(cls, attr, property(getter, setter))
        return cls
    return wrapper

def add_undetermined_properties(**typed_attrs):
    """
    Class decorator that dynamically adds properties which must be either:
    - Of a specified type (e.g., int, str), or
    - An 'Unknown' object (checked via is_undetermined)
    """
    def wrapper(cls):
        for attr_name, accepted_type in typed_attrs.items():
            private_attr = "_" + attr_name

            def getter(self, attr=private_attr):
                return getattr(self, attr)

            def setter(self:UndeterminedContainer, value, attr_name=private_attr, accepted_type=accepted_type):
                self._set_undetermined_attr(attr_name, value, accepted_type)

            setattr(cls, attr_name, property(getter, setter))
        return cls
    return wrapper


class BoolContainer:
    def _set_bool_attr(self, attr_name: str, value: any):
        ensure_all_bools([value], return_false_on_error=False)
        setattr(self, attr_name, value)

class UndeterminedContainer:
    """
    A base class for objects that can have attributes which are either
    of a specific type or an 'Unknown' object.
    """
    def _set_undetermined_attr(self, attr_name: str, value: any, accepted_type: type):
        if not is_undetermined(value) and not isinstance(value, accepted_type)  :
            raise ValueError(f"Invalid value for '{attr_name}': {value} (must be {accepted_type.__name__} or Unknown)")
        setattr(self, attr_name, value)

class DualContainer(BoolContainer, UndeterminedContainer):
    """
    A base class that combines both BoolContainer and UndeterminedContainer.
    This allows for attributes that can be either boolean or of a specific type,
    or an 'Unknown' object.
    """
    def _set_bool_attr(self, attr_name: str, value: any):
        super()._set_bool_attr(attr_name, value)

    def _set_undetermined_attr(self, attr_name: str, value: any, accepted_type: type):
        super()._set_undetermined_attr(attr_name, value, accepted_type)

