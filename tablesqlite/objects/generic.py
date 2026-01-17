"""Generic utility classes and functions.

This module provides the Unknown class for representing undetermined values
and utility functions for string quoting.
"""

from typing import Any

DOUBLE_QUOTE = '"'


def ensure_quoted(s: str, quote: str = DOUBLE_QUOTE) -> str:
    """Ensure that a string is enclosed in quotes.

    If the string already starts and ends with the specified quote,
    it is returned unchanged. Otherwise, the string is enclosed in
    the specified quote.

    Args:
        s: The string to be quoted.
        quote: The quote character to use (default is double quote).

    Returns:
        The quoted string.
    """
    if s.startswith(quote) and s.endswith(quote):
        return s
    return f"{quote}{s}{quote}"


class Unknown:
    """A class to represent an unknown value.

    This is used to indicate that a value is not known or not applicable.
    It provides a consistent way to handle missing or undefined values
    in table and column definitions.

    Args:
        name: A descriptive name for this unknown value.
    """

    def __init__(self, name: str) -> None:
        """Initialize an Unknown instance with a name."""
        self.name = name

    def __repr__(self) -> str:
        """Return a string representation of the Unknown instance."""
        return f"Unknown({self.name})"

    def __str__(self) -> str:
        """Return the name of the Unknown instance as a string."""
        return self.name

    def __iter__(self) -> Any:
        """Allow iteration over the Unknown instance, yielding nothing."""
        return iter([])

    def __eq__(self, other: Any) -> bool:
        """Check equality with another object.

        Two Unknown instances are considered equal if they have the same name.

        Args:
            other: The object to compare with.

        Returns:
            True if the objects are equal, False otherwise.
        """
        if isinstance(other, Unknown):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        """Return a hash value for the Unknown instance.

        This allows Unknown instances to be used in sets or as dictionary keys.

        Returns:
            Hash value based on the name.
        """
        return hash(self.name)


def is_undetermined(item: Any) -> bool:
    """Check if the item is an instance of Unknown or None.

    Args:
        item: The item to check.

    Returns:
        True if the item is Unknown or None, False otherwise.
    """
    return isinstance(item, Unknown) or item is None


# Singleton unknown instance for general use
unknown = Unknown("unknown")
