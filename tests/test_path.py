"""Tests for validation/path.py module."""

import pytest

from tablesqlite.validation.path import (
    ILLEGAL_CHARS_PATTERN,
    WINDOWS_RESERVED_NAMES,
    validate_database_path,
    validate_file_name,
)


class TestValidateFileName:
    """Tests for validate_file_name function."""

    def test_validate_file_name_valid(self) -> None:
        """Test validate_file_name with valid names."""
        assert validate_file_name("test.db") is True
        assert validate_file_name("my_database.db") is True
        assert validate_file_name("data123.db") is True

    def test_validate_file_name_empty(self) -> None:
        """Test validate_file_name with empty name."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_file_name("")

    def test_validate_file_name_whitespace_only(self) -> None:
        """Test validate_file_name with whitespace only."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_file_name("   ")

    def test_validate_file_name_starts_with_dot(self) -> None:
        """Test validate_file_name with name starting with dot."""
        with pytest.raises(ValueError, match="cannot start or end with a dot"):
            validate_file_name(".hidden")

    def test_validate_file_name_ends_with_dot(self) -> None:
        """Test validate_file_name with name ending with dot."""
        with pytest.raises(ValueError, match="cannot start or end with a dot"):
            validate_file_name("file.")

    def test_validate_file_name_just_slash(self) -> None:
        r"""Test validate_file_name with just a slash.

        Note: Path separator behavior differs by platform:
        - On Windows: both / and \ are separators, so both become empty strings
        - On Unix/Linux: only / is a separator, \ stays as-is
        """
        import platform

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_file_name("/")

        # On Windows, backslash is also a separator, so it becomes empty
        # On Unix/Linux, backslash is not a separator, so it stays as "\"
        if platform.system() == "Windows":
            with pytest.raises(ValueError, match="cannot be empty"):
                validate_file_name("\\")
        else:
            with pytest.raises(ValueError, match="just a slash"):
                validate_file_name("\\")

    def test_validate_file_name_illegal_chars(self) -> None:
        """Test validate_file_name with illegal characters."""
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file<name")
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file>name")
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file:name")
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name('file"name')
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file|name")
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file?name")
        with pytest.raises(ValueError, match="illegal characters"):
            validate_file_name("file*name")

    def test_validate_file_name_windows_reserved(self) -> None:
        """Test validate_file_name with Windows reserved names."""
        for reserved in ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            with pytest.raises(ValueError, match="reserved on Windows"):
                validate_file_name(reserved)
            # Case insensitive
            with pytest.raises(ValueError, match="reserved on Windows"):
                validate_file_name(reserved.lower())

    def test_validate_file_name_too_long(self) -> None:
        """Test validate_file_name with name too long."""
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_file_name("a" * 256)

    def test_validate_file_name_return_false_on_error(self) -> None:
        """Test validate_file_name with return_false_on_error=True."""
        assert validate_file_name("", return_false_on_error=True) is False
        assert validate_file_name(".hidden", return_false_on_error=True) is False
        assert validate_file_name("CON", return_false_on_error=True) is False

    def test_validate_file_name_non_string(self) -> None:
        """Test validate_file_name with non-string."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_file_name(123)  # type: ignore

    def test_validate_file_name_remove_suffix(self) -> None:
        """Test validate_file_name with remove_suffix=True."""
        assert validate_file_name("test.db", remove_suffix=True) is True
        # With suffix removed, .hidden becomes hidden which is valid
        # Actually after removal of suffix, if there's no suffix it stays the same
        assert validate_file_name("test", remove_suffix=True) is True


class TestValidateDatabasePath:
    """Tests for validate_database_path function."""

    def test_validate_database_path_valid(self) -> None:
        """Test validate_database_path with valid paths."""
        assert validate_database_path("test.db") is True
        assert validate_database_path("/path/to/test.db") is True
        assert validate_database_path("./data/test.db") is True

    def test_validate_database_path_no_db_extension(self) -> None:
        """Test validate_database_path without .db extension."""
        with pytest.raises(ValueError, match="must end with '.db'"):
            validate_database_path("test.sqlite")
        with pytest.raises(ValueError, match="must end with '.db'"):
            validate_database_path("test")

    def test_validate_database_path_none(self) -> None:
        """Test validate_database_path with None."""
        with pytest.raises(ValueError, match="cannot be None or Unknown"):
            validate_database_path(None)  # type: ignore

    def test_validate_database_path_non_string(self) -> None:
        """Test validate_database_path with non-string."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_database_path(123)  # type: ignore

    def test_validate_database_path_return_false_on_error(self) -> None:
        """Test validate_database_path with return_false_on_error=True."""
        result1 = validate_database_path(
            "test.sqlite", return_false_on_error=True
        )
        assert result1 is False
        assert validate_database_path("", return_false_on_error=True) is False


class TestConstants:
    """Tests for module constants."""

    def test_windows_reserved_names(self) -> None:
        """Test WINDOWS_RESERVED_NAMES contains expected values."""
        assert "CON" in WINDOWS_RESERVED_NAMES
        assert "PRN" in WINDOWS_RESERVED_NAMES
        assert "AUX" in WINDOWS_RESERVED_NAMES
        assert "NUL" in WINDOWS_RESERVED_NAMES
        assert "COM1" in WINDOWS_RESERVED_NAMES
        assert "LPT1" in WINDOWS_RESERVED_NAMES

    def test_illegal_chars_pattern(self) -> None:
        """Test ILLEGAL_CHARS_PATTERN matches expected characters."""
        assert ILLEGAL_CHARS_PATTERN.search("<") is not None
        assert ILLEGAL_CHARS_PATTERN.search(">") is not None
        assert ILLEGAL_CHARS_PATTERN.search(":") is not None
        assert ILLEGAL_CHARS_PATTERN.search('"') is not None
        assert ILLEGAL_CHARS_PATTERN.search("/") is not None
        assert ILLEGAL_CHARS_PATTERN.search("\\") is not None
        assert ILLEGAL_CHARS_PATTERN.search("|") is not None
        assert ILLEGAL_CHARS_PATTERN.search("?") is not None
        assert ILLEGAL_CHARS_PATTERN.search("*") is not None
        # Valid characters should not match
        assert ILLEGAL_CHARS_PATTERN.search("abc") is None
        assert ILLEGAL_CHARS_PATTERN.search("123") is None
