from __future__ import annotations
from typing import Any

double_quote = '"'
def ensure_quoted(s: str, quote:str = double_quote) -> str:
    """
    Ensure that a string is enclosed in quotes.
    If the string already starts and ends with the specified quote, it is returned unchanged.
    Otherwise, the string is enclosed in the specified quote.
    
    Args:
        s (str): The string to be quoted.
        quote (str): The quote character to use (default is double_quote).
    
    Returns:
        str: The quoted string.
    """
    if s.startswith(quote) and s.endswith(quote):
        return s
    return f"{quote}{s}{quote}"

class Unknown:
    """
    A class to represent an unknown value.
    This is used to indicate that a value is not known or not applicable.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Unknown({self.name})"

    def __str__(self):
        return self.name
    def __iter__(self):
        """
        Allow iteration over the Unknown instance, yielding nothing.
        """
        return iter([])
    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another object.
        Two Unknown instances are considered equal if they have the same name.
        """
        if isinstance(other, Unknown):
            return self.name == other.name
        return False
    def __hash__(self) -> int:
        """
        Return a hash value for the Unknown instance based on its name.
        This allows Unknown instances to be used in sets or as dictionary keys.
        """
        return hash(self.name)
def is_undetermined(item:Any) -> bool:
    """
    Check if the item is an instance of Unknown.
    """
    return isinstance(item, Unknown) or item is None

unknown = Unknown("unknown")