"""Tests for utility functions in tablesqlite.utils module."""

from enum import IntEnum

import pytest

from tablesqlite import (
    SQLColumnInfo,
    SQLTableInfo,
    convert_enum_value,
    generate_migration,
    validate_foreign_keys,
)


class TestConvertEnumValue:
    """Test cases for convert_enum_value function."""

    def test_convert_enum_value_from_int(self) -> None:
        """Test converting an integer to IntEnum."""
        class Status(IntEnum):
            PENDING = 1
            ACTIVE = 2
            COMPLETED = 3

        result = convert_enum_value(1, Status)
        assert result == Status.PENDING
        assert isinstance(result, Status)

    def test_convert_enum_value_from_string(self) -> None:
        """Test converting a string to IntEnum."""
        class Priority(IntEnum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3

        result = convert_enum_value("2", Priority)
        assert result == Priority.MEDIUM
        assert isinstance(result, Priority)

    def test_convert_enum_value_from_enum(self) -> None:
        """Test converting an IntEnum to itself."""
        class Color(IntEnum):
            RED = 1
            GREEN = 2
            BLUE = 3

        result = convert_enum_value(Color.GREEN, Color)
        assert result == Color.GREEN
        assert isinstance(result, Color)

    def test_convert_enum_value_invalid_string(self) -> None:
        """Test error when string cannot be converted to int."""
        class Status(IntEnum):
            PENDING = 1

        with pytest.raises(ValueError, match="Cannot convert string"):
            convert_enum_value("invalid", Status)

    def test_convert_enum_value_invalid_int(self) -> None:
        """Test error when int is not a valid enum value."""
        class Status(IntEnum):
            PENDING = 1
            ACTIVE = 2

        with pytest.raises(ValueError, match="not a valid Status"):
            convert_enum_value(99, Status)

    def test_convert_enum_value_not_intenum(self) -> None:
        """Test error when enum_class is not an IntEnum subclass."""
        class NotIntEnum:
            VALUE = 1

        with pytest.raises(TypeError, match="must be an IntEnum subclass"):
            convert_enum_value(1, NotIntEnum)  # type: ignore

    def test_convert_enum_value_zero_value(self) -> None:
        """Test converting zero value to IntEnum."""
        class Status(IntEnum):
            INACTIVE = 0
            ACTIVE = 1

        result = convert_enum_value(0, Status)
        assert result == Status.INACTIVE

    def test_convert_enum_value_negative_value(self) -> None:
        """Test converting negative value to IntEnum."""
        class Direction(IntEnum):
            LEFT = -1
            CENTER = 0
            RIGHT = 1

        result = convert_enum_value(-1, Direction)
        assert result == Direction.LEFT


class TestValidateForeignKeys:
    """Test cases for validate_foreign_keys function."""

    def test_validate_foreign_keys_valid_inline(self) -> None:
        """Test validation with valid inline foreign key."""
        users = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])
        posts = SQLTableInfo("posts", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo(
                "user_id",
                "INTEGER",
                foreign_key={"table": "users", "column": "id"}
            )
        ])

        tables = {"users": users, "posts": posts}
        errors = validate_foreign_keys(posts, tables)

        assert errors == []

    def test_validate_foreign_keys_missing_table_inline(self) -> None:
        """Test validation with missing referenced table in inline foreign key."""
        posts = SQLTableInfo("posts", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo(
                "user_id",
                "INTEGER",
                foreign_key={"table": "users", "column": "id"}
            )
        ])

        tables = {"posts": posts}
        errors = validate_foreign_keys(posts, tables)

        assert len(errors) == 1
        assert "user_id" in errors[0]
        assert "users" in errors[0]

    def test_validate_foreign_keys_valid_table_level(self) -> None:
        """Test validation with valid table-level foreign key."""
        customers = SQLTableInfo("customers", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])
        stores = SQLTableInfo("stores", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])
        orders = SQLTableInfo(
            "orders",
            [
                SQLColumnInfo("id", "INTEGER", primary_key=True),
                SQLColumnInfo("customer_id", "INTEGER"),
                SQLColumnInfo("store_id", "INTEGER"),
            ],
            foreign_keys=[
                {
                    "columns": ["customer_id", "store_id"],
                    "ref_table": "customer_stores",
                    "ref_columns": ["customer_id", "store_id"]
                }
            ]
        )

        customer_stores = SQLTableInfo("customer_stores", [
            SQLColumnInfo("customer_id", "INTEGER", primary_key=True),
            SQLColumnInfo("store_id", "INTEGER", primary_key=True)
        ])

        tables = {
            "customers": customers,
            "stores": stores,
            "orders": orders,
            "customer_stores": customer_stores
        }
        errors = validate_foreign_keys(orders, tables)

        assert errors == []

    def test_validate_foreign_keys_missing_table_table_level(self) -> None:
        """Test validation with missing referenced table in table-level foreign key."""
        orders = SQLTableInfo(
            "orders",
            [
                SQLColumnInfo("id", "INTEGER", primary_key=True),
                SQLColumnInfo("customer_id", "INTEGER"),
            ],
            foreign_keys=[
                {
                    "columns": ["customer_id"],
                    "ref_table": "customers",
                    "ref_columns": ["id"]
                }
            ]
        )

        tables = {"orders": orders}
        errors = validate_foreign_keys(orders, tables)

        assert len(errors) == 1
        assert "customers" in errors[0]

    def test_validate_foreign_keys_multiple_errors(self) -> None:
        """Test validation with multiple foreign key errors."""
        orders = SQLTableInfo(
            "orders",
            [
                SQLColumnInfo("id", "INTEGER", primary_key=True),
                SQLColumnInfo(
                    "user_id",
                    "INTEGER",
                    foreign_key={"table": "users", "column": "id"}
                ),
                SQLColumnInfo(
                    "product_id",
                    "INTEGER",
                    foreign_key={"table": "products", "column": "id"}
                ),
            ],
            foreign_keys=[
                {
                    "columns": ["user_id"],
                    "ref_table": "customers",
                    "ref_columns": ["id"]
                }
            ]
        )

        tables = {"orders": orders}
        errors = validate_foreign_keys(orders, tables)

        assert len(errors) == 3
        assert any("users" in err for err in errors)
        assert any("products" in err for err in errors)
        assert any("customers" in err for err in errors)

    def test_validate_foreign_keys_no_foreign_keys(self) -> None:
        """Test validation with table that has no foreign keys."""
        users = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])

        tables = {"users": users}
        errors = validate_foreign_keys(users, tables)

        assert errors == []


class TestGenerateMigration:
    """Test cases for generate_migration function."""

    def test_generate_migration_add_column(self) -> None:
        """Test migration generation when adding a column."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])
        new = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT"),
            SQLColumnInfo("email", "TEXT")
        ])

        migrations = generate_migration(old, new)

        assert len(migrations) == 1
        assert "ADD COLUMN" in migrations[0][0]
        assert "email" in migrations[0][0]

    def test_generate_migration_add_multiple_columns(self) -> None:
        """Test migration generation when adding multiple columns."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])
        new = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("email", "TEXT"),
            SQLColumnInfo("name", "TEXT")
        ])

        migrations = generate_migration(old, new)

        # Should have 2 ADD COLUMN statements
        add_cols = [m for m in migrations if "ADD COLUMN" in m[0]]
        assert len(add_cols) == 2

    def test_generate_migration_drop_column(self) -> None:
        """Test migration generation when dropping a column."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT"),
            SQLColumnInfo("email", "TEXT")
        ])
        new = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])

        migrations = generate_migration(old, new)

        # Should have a comment about DROP COLUMN limitation
        assert len(migrations) >= 1
        assert any("DROP COLUMN" in m[0] for m in migrations)
        assert any("3.35.0" in m[0] or "email" in m[0] for m in migrations)

    def test_generate_migration_rename_table(self) -> None:
        """Test migration generation when renaming a table."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])
        new = SQLTableInfo("customers", [
            SQLColumnInfo("id", "INTEGER", primary_key=True)
        ])

        migrations = generate_migration(old, new)

        assert len(migrations) >= 1
        assert "RENAME TO" in migrations[0][0]
        assert "customers" in migrations[0][0]

    def test_generate_migration_modify_column(self) -> None:
        """Test migration generation when modifying a column."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])
        new = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT", not_null=True)
        ])

        migrations = generate_migration(old, new)

        # Should have a comment about SQLite limitation
        assert len(migrations) >= 1
        has_column_modification_warning = any(
            "Cannot modify column" in m[0] or "recreation" in m[0]
            for m in migrations
        )
        assert has_column_modification_warning, (
            "Expected migration to include warning about column modification"
        )

    def test_generate_migration_no_changes(self) -> None:
        """Test migration generation when there are no changes."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])
        new = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT")
        ])

        migrations = generate_migration(old, new)

        # Should have no migrations
        assert len(migrations) == 0

    def test_generate_migration_foreign_key_changes(self) -> None:
        """Test migration generation when foreign keys change."""
        old = SQLTableInfo("posts", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("user_id", "INTEGER")
        ])
        new = SQLTableInfo(
            "posts",
            [
                SQLColumnInfo("id", "INTEGER", primary_key=True),
                SQLColumnInfo("user_id", "INTEGER")
            ],
            foreign_keys=[
                {
                    "columns": ["user_id"],
                    "ref_table": "users",
                    "ref_columns": ["id"]
                }
            ]
        )

        migrations = generate_migration(old, new)

        # Should have a comment about foreign key changes
        assert len(migrations) >= 1
        has_foreign_key_recreation_warning = any(
            "Foreign key" in m[0] and "recreation" in m[0]
            for m in migrations
        )
        assert has_foreign_key_recreation_warning, (
            "Expected migration to include warning about foreign key changes"
        )

    def test_generate_migration_complex_changes(self) -> None:
        """Test migration generation with multiple types of changes."""
        old = SQLTableInfo("users", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("old_field", "TEXT")
        ])
        new = SQLTableInfo("customers", [
            SQLColumnInfo("id", "INTEGER", primary_key=True),
            SQLColumnInfo("name", "TEXT"),
            SQLColumnInfo("email", "TEXT")
        ])

        migrations = generate_migration(old, new)

        # Should have rename table, add columns, and drop column
        assert len(migrations) >= 3
        assert any("RENAME TO" in m[0] for m in migrations)
        assert any("ADD COLUMN" in m[0] for m in migrations)
