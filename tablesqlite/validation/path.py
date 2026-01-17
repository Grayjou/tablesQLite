"""Database path validation utilities.

This module provides functions for validating database file paths.
"""

import os
import re

from ..objects.generic import is_undetermined

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

ILLEGAL_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


def validate_file_name(
    file_name: str,
    *,
    return_false_on_error: bool = False,
    remove_suffix: bool = False,
) -> bool:
    """Validate a file name.

    Args:
        file_name: The file name to validate.
        return_false_on_error: If True, return False instead of raising an error.
        remove_suffix: If True, remove the file suffix before validation.

    Returns:
        True if the file name is valid.

    Raises:
        ValueError: If the file name is invalid and return_false_on_error is False.
    """
    try:
        if not isinstance(file_name, str):
            raise ValueError("file_name must be a string")

        file_name = os.path.basename(file_name)

        if remove_suffix:
            dot_index = file_name.rfind(".")
            if dot_index > 0:
                file_name = file_name[:dot_index]

        stripped_name = file_name.strip()

        if not stripped_name:
            raise ValueError("file_name cannot be empty or whitespace only")
        if stripped_name.startswith(".") or stripped_name.endswith("."):
            raise ValueError("file_name cannot start or end with a dot")
        if stripped_name in ("/", "\\"):
            raise ValueError("file_name cannot be just a slash")
        if ILLEGAL_CHARS_PATTERN.search(stripped_name):
            raise ValueError(
                'file_name contains illegal characters (e.g. < > : " / \\ | ? *)'
            )
        if stripped_name.upper() in WINDOWS_RESERVED_NAMES:
            raise ValueError(f"file_name '{file_name}' is reserved on Windows")
        if len(stripped_name) > 255:
            raise ValueError("file_name exceeds maximum length (255 characters)")

    except ValueError as e:
        if return_false_on_error:
            return False
        raise e

    return True


def validate_database_path(
    database_path: str,
    *,
    return_false_on_error: bool = False,
) -> bool:
    """Validate a database file path.

    Args:
        database_path: The database path to validate.
        return_false_on_error: If True, return False instead of raising an error.

    Returns:
        True if the database path is valid.

    Raises:
        ValueError: If the database path is invalid and return_false_on_error is False.
    """
    try:
        if is_undetermined(database_path):
            raise ValueError("database_path cannot be None or Unknown")

        if not isinstance(database_path, str):
            raise ValueError("database_path must be a string")

        file_name = os.path.basename(database_path)

        if not file_name.endswith(".db"):
            raise ValueError("database_path must end with '.db'")

        if not validate_file_name(
            file_name, return_false_on_error=False, remove_suffix=True
        ):
            raise ValueError(
                "database_path contains an invalid file name before '.db'"
            )

    except ValueError as e:
        if return_false_on_error:
            return False
        raise e

    return True

