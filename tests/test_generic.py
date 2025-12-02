"""Tests for objects/generic.py module."""


from tablesqlite.objects.generic import (
    DOUBLE_QUOTE,
    Unknown,
    ensure_quoted,
    is_undetermined,
    unknown,
)


class TestUnknown:
    """Tests for the Unknown class."""

    def test_unknown_init(self) -> None:
        """Test Unknown initialization."""
        u = Unknown("test")
        assert u.name == "test"

    def test_unknown_repr(self) -> None:
        """Test Unknown __repr__."""
        u = Unknown("my_name")
        assert repr(u) == "Unknown(my_name)"

    def test_unknown_str(self) -> None:
        """Test Unknown __str__."""
        u = Unknown("my_name")
        assert str(u) == "my_name"

    def test_unknown_iter(self) -> None:
        """Test Unknown __iter__ yields nothing."""
        u = Unknown("test")
        assert list(u) == []

    def test_unknown_eq_same_name(self) -> None:
        """Test Unknown equality with same name."""
        u1 = Unknown("test")
        u2 = Unknown("test")
        assert u1 == u2

    def test_unknown_eq_different_name(self) -> None:
        """Test Unknown inequality with different name."""
        u1 = Unknown("test1")
        u2 = Unknown("test2")
        assert u1 != u2

    def test_unknown_eq_non_unknown(self) -> None:
        """Test Unknown inequality with non-Unknown objects."""
        u = Unknown("test")
        assert u != "test"
        assert u != 123
        assert u != None  # noqa: E711

    def test_unknown_hash(self) -> None:
        """Test Unknown hash."""
        u1 = Unknown("test")
        u2 = Unknown("test")
        assert hash(u1) == hash(u2)

        u3 = Unknown("other")
        # Different names should typically have different hashes
        # (not guaranteed but likely)
        assert hash(u1) != hash(u3)

    def test_unknown_can_be_used_in_set(self) -> None:
        """Test Unknown can be used in sets."""
        u1 = Unknown("test")
        u2 = Unknown("test")
        u3 = Unknown("other")
        s = {u1, u2, u3}
        assert len(s) == 2

    def test_unknown_can_be_used_as_dict_key(self) -> None:
        """Test Unknown can be used as dictionary key."""
        u = Unknown("test")
        d = {u: "value"}
        assert d[u] == "value"


class TestIsUndetermined:
    """Tests for is_undetermined function."""

    def test_is_undetermined_unknown(self) -> None:
        """Test is_undetermined with Unknown."""
        u = Unknown("test")
        assert is_undetermined(u) is True

    def test_is_undetermined_none(self) -> None:
        """Test is_undetermined with None."""
        assert is_undetermined(None) is True

    def test_is_undetermined_regular_values(self) -> None:
        """Test is_undetermined with regular values."""
        assert is_undetermined("string") is False
        assert is_undetermined(123) is False
        assert is_undetermined(0) is False
        assert is_undetermined("") is False
        assert is_undetermined([]) is False
        assert is_undetermined({}) is False

    def test_is_undetermined_singleton(self) -> None:
        """Test is_undetermined with the singleton unknown."""
        assert is_undetermined(unknown) is True


class TestEnsureQuoted:
    """Tests for ensure_quoted function."""

    def test_ensure_quoted_unquoted(self) -> None:
        """Test ensure_quoted with unquoted string."""
        assert ensure_quoted("test") == '"test"'

    def test_ensure_quoted_already_quoted(self) -> None:
        """Test ensure_quoted with already quoted string."""
        assert ensure_quoted('"test"') == '"test"'

    def test_ensure_quoted_custom_quote(self) -> None:
        """Test ensure_quoted with custom quote character."""
        assert ensure_quoted("test", "'") == "'test'"
        assert ensure_quoted("'test'", "'") == "'test'"

    def test_ensure_quoted_empty_string(self) -> None:
        """Test ensure_quoted with empty string."""
        assert ensure_quoted("") == '""'

    def test_ensure_quoted_partial_quotes(self) -> None:
        """Test ensure_quoted with partial quotes."""
        # Only start quote
        assert ensure_quoted('"test') == '""test"'
        # Only end quote
        assert ensure_quoted('test"') == '"test""'

    def test_double_quote_constant(self) -> None:
        """Test DOUBLE_QUOTE constant value."""
        assert DOUBLE_QUOTE == '"'


class TestUnknownSingleton:
    """Tests for the unknown singleton."""

    def test_unknown_singleton_exists(self) -> None:
        """Test unknown singleton exists and has correct name."""
        assert isinstance(unknown, Unknown)
        assert unknown.name == "unknown"

    def test_unknown_singleton_is_undetermined(self) -> None:
        """Test unknown singleton is detected as undetermined."""
        assert is_undetermined(unknown) is True
