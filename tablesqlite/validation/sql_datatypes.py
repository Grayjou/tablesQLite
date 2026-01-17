"""SQL data type validation utilities.

This module provides functions and classes for validating SQL data types.
"""

from __future__ import annotations

from sortedcontainers import SortedDict


def upper_before_bracket(s: str) -> str:
    """Convert the part before an opening bracket to uppercase.

    Args:
        s: The string to convert.

    Returns:
        The string with the part before '(' in uppercase.
    """
    if not s:
        return s
    partition = s.partition("(")
    return partition[0].upper() + partition[1] + partition[2]


ALL_TYPES = (
    "BIGINT(size)",
    "BINARY(size)",
    "BIT(size)",
    "BLOB",
    "BOOL",
    "BOOLEAN",
    "CHAR(size)",
    "DATE",
    "DATETIME(fsp)",
    "DEC(p)",
    "DECIMAL(p)",
    "DOUBLE PRECISION(p)",
    "DOUBLE(p)",
    "ENUM(...)",
    "FLOAT(p)",
    "INT(size)",
    "INTEGER(size)",
    "LONGBLOB",
    "LONGTEXT",
    "MEDIUMBLOB",
    "MEDIUMINT(size)",
    "MEDIUMTEXT",
    "REAL(p)",
    "SET(...)",
    "SMALLINT(size)",
    "TEXT",
    "TIME(fsp)",
    "TIMESTAMP(fsp)",
    "TINYBLOB",
    "TINYINT(size)",
    "TINYTEXT",
    "VARBINARY(size)",
    "VARCHAR(size)",
    "YEAR",
)


def bracket_tuple_from_str(data_str: str) -> tuple[str, tuple[str, ...]]:
    """Parse a data type string into a tuple of (type, args).

    Args:
        data_str: The data type string to parse.

    Returns:
        A tuple of (type_name, args_tuple).
    """
    if "(" not in data_str:
        return data_str.strip(), ()
    type_, args_str = data_str.split("(", 1)
    args_str = args_str.rstrip(")")
    args = tuple(arg.strip() for arg in args_str.split(",") if arg.strip())
    return type_.strip(), args


PLACEHOLDER_INT_KEYS = {"size", "fsp", "p"}


def match_bracket_tuple(
    data_str: str,
    pairs: set[tuple[str, tuple[str, ...]]] | None = None,
) -> bool:
    """Check if a data type string matches any of the predefined types.

    Args:
        data_str: The data type string to check.
        pairs: Set of valid (type, args) tuples.

    Returns:
        True if the data type matches a valid type.
    """
    if not pairs:
        return False
    type_, args = bracket_tuple_from_str(data_str)
    type_ = type_.strip().upper()

    for datatype, expected_args in pairs:
        if type_ != datatype.strip().upper():
            continue

        # Wildcard: accept anything
        if expected_args == ("...",):
            return True

        # Allow fewer args than expected (e.g., FLOAT → FLOAT(p))
        if len(args) > len(expected_args):
            return False

        for arg, expected in zip(args, expected_args):
            if expected == "...":
                continue
            if expected in PLACEHOLDER_INT_KEYS and not arg.isdigit():
                return False

        return True  # Valid even with missing optional args
    return False


def is_list_of_pairs(lst: list) -> bool:
    """Check if the given list contains pairs of elements.

    Args:
        lst: The list to check.

    Returns:
        True if all items are 2-element tuples.
    """
    return all(isinstance(item, tuple) and len(item) == 2 for item in lst)


class Validator(SortedDict):
    """A validator for SQL data types.

    This class maintains a sorted dictionary of valid SQL data types
    and provides methods to validate and manage them.
    """

    def __init__(self) -> None:
        """Initialize the validator with default SQL data types."""
        super().__init__({bracket_tuple_from_str(string) for string in ALL_TYPES})

    def validate_type(self, data_str: str) -> bool:
        """Validate if the given data type string is valid.

        Args:
            data_str: The data type string to validate.

        Returns:
            True if the data type is valid, False otherwise.
        """
        return match_bracket_tuple(data_str, self.items())

    def add_type(self, data_str: str) -> None:
        """Add a new data type to the validator.

        Args:
            data_str: The data type string to add.

        Raises:
            TypeError: If data_str is not a string.
        """
        if not isinstance(data_str, str):
            raise TypeError("data_str must be a string")
        type_, args = bracket_tuple_from_str(data_str)
        self[type_.upper()] = args

    def remove_type(self, data_str: str) -> None:
        """Remove a data type from the validator.

        Args:
            data_str: The data type string to remove.

        Raises:
            TypeError: If data_str is not a string.
        """
        if not isinstance(data_str, str):
            raise TypeError("data_str must be a string")
        type_, _ = bracket_tuple_from_str(data_str)
        self.pop(type_.upper(), None)


_validator: Validator | None = None


def get_validator() -> Validator:
    """Get the singleton instance of the Validator.

    Returns:
        The singleton Validator instance.
    """
    global _validator
    if _validator is None:
        _validator = Validator()
    return _validator


def validate_data_type(data_str: str) -> bool:
    """Validate a SQL data type string.

    Args:
        data_str: The data type string to validate.

    Returns:
        True if the data type is valid.

    Raises:
        ValueError: If the data type is invalid.
    """
    if not get_validator().validate_type(data_str):
        raise ValueError(f"Invalid data type: {data_str}")
    return True
