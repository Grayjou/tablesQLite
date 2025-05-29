from __future__ import annotations
from typing import Union, Iterable

def ensure_bool(value, *, return_false_on_error: bool = False) -> bool:
    """
    Ensure the value is a boolean. If not, raise ValueError or return False based on the flag.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value.lower() in ('true', '1'):
            return True
        elif value.lower() in ('false', '0'):
            return False
    elif isinstance(value, int):
        if value in (1, True):
            return True
        elif value in (0, False):
            return False
    if return_false_on_error:
        return False
    raise ValueError(f"Expected a boolean value, got {value!r}")

def ensure_all_bools(
    values: Iterable[Union[bool, str, int]], 
    *, 
    return_false_on_error: bool = False
) -> list[bool]:
    """
    Ensure all values in the iterable are booleans. If not, raise ValueError or return False based on the flag.
    """
    result = []
    for value in values:
        try:
            result.append(ensure_bool(value, return_false_on_error=return_false_on_error))
        except ValueError as e:
            if return_false_on_error:
                result.append(False)
            else:
                raise ValueError(f"Invalid boolean value in list: {value!r}") from e
    return result