# TODO List - Future Enhancements

This document tracks planned enhancements and improvements for tablesqlite.

## High Priority

### 1. Advanced Migration Support
- [ ] Implement table recreation pattern for complex migrations
  - Create temporary table with new schema
  - Copy data with column mapping
  - Drop old table and rename new one
- [ ] Add migration history tracking
- [ ] Support for reversible migrations (up/down)
- [ ] Batch migration executor with transaction support

### 2. Index Management
- [ ] Add `SQLIndexInfo` class to represent indexes
- [ ] Generate CREATE INDEX / DROP INDEX statements
- [ ] Parse existing indexes from schema
- [ ] Support for unique, partial, and expression indexes
- [ ] Index validation and optimization recommendations

### 3. Enhanced Schema Introspection
- [ ] Extend schema parsing to handle more complex SQL features
- [ ] Parse triggers from schema
- [ ] Parse views from schema
- [ ] Extract and validate CHECK constraints
- [ ] Support for STRICT tables (SQLite 3.37.0+)

## Medium Priority

### 4. Data Type Extensions
- [ ] Custom type registry for domain-specific types
- [ ] Type conversion helpers for common patterns (JSON, datetime, UUID)
- [ ] Type validation improvements
- [ ] Support for SQLite JSON1 extension types

### 5. Constraint Improvements
- [ ] Support for DEFERRABLE foreign keys
- [ ] Named constraints for better error messages
- [ ] Constraint validation at Python level before SQL execution
- [ ] ON DELETE/ON UPDATE cascade actions for foreign keys (already partially supported)

### 6. Query Builder Enhancements
- [ ] Generate SELECT queries with JOIN support
- [ ] Query templates for common patterns
- [ ] Subquery support in table definitions
- [ ] CTE (Common Table Expression) support

### 7. Testing and Validation
- [ ] Schema validation mode (check against actual database)
- [ ] Test data generators based on column constraints
- [ ] Schema migration testing utilities
- [ ] Performance benchmarking tools

## Low Priority

### 8. Documentation Improvements
- [ ] Interactive tutorial with examples
- [ ] Video walkthroughs for common use cases
- [ ] Best practices guide for schema design
- [ ] Migration guide from other ORMs/schema managers

### 9. Developer Experience
- [ ] CLI tool for schema operations
- [ ] Schema visualization (generate ER diagrams)
- [ ] IDE integration (VS Code extension)
- [ ] Schema diff viewer (HTML/CLI output)

### 10. Performance Optimizations
- [ ] Lazy column validation
- [ ] Cache compiled SQL statements
- [ ] Bulk operation optimizations
- [ ] Memory usage profiling and optimization

## SQLite Limitations to Consider

These features are limited by SQLite's capabilities and would require workarounds:

1. **Column Modification**: SQLite doesn't support ALTER COLUMN. Requires table recreation.
2. **DROP COLUMN**: Only supported in SQLite 3.35.0+. Older versions need table recreation.
3. **Constraint Modification**: Cannot add/remove constraints except via table recreation.
4. **Rename Constraints**: Not supported. Would need table recreation.
5. **Check Constraint Names**: Cannot be explicitly named in SQLite.

## Related Projects Integration

### Integration with recordsQL (Already Supported)
- [x] Basic integration for DML operations
- [ ] Enhanced query builder integration
- [ ] Transaction management helpers
- [ ] Batch operation support

### Potential New Integrations
- [ ] Integration with Alembic for migrations
- [ ] Integration with SQLAlchemy for ORM features
- [ ] Integration with Pydantic for data validation
- [ ] Integration with FastAPI for auto-generated APIs

## Community Requests

Track issues and feature requests from users:
- [ ] Monitor GitHub issues for common feature requests
- [ ] Survey users for most-wanted features
- [ ] Prioritize based on user impact and implementation complexity

## Technical Debt

Items to address for code quality and maintainability:
- [ ] Increase test coverage to 100%
- [ ] Add property-based testing with Hypothesis
- [ ] Performance benchmarks and regression tests
- [ ] Documentation coverage for all public APIs
- [ ] Type hint coverage verification

## Version Planning

### v0.2.0 (Next Minor Release)
- Enhanced utilities (convert_enum_value, validate_foreign_keys, generate_migration)
- Improved documentation
- Additional test coverage

### v0.3.0
- Index management support
- Enhanced migration tools
- CLI tool for common operations

### v1.0.0 (Stable Release)
- Complete feature set for DDL operations
- Comprehensive documentation
- Production-ready migration tools
- Strong backward compatibility guarantees

## Contributing

We welcome contributions! If you'd like to work on any of these features:
1. Open an issue to discuss the approach
2. Fork the repository
3. Implement the feature with tests
4. Submit a pull request

For implementation guidelines, see CONTRIBUTING.md (to be created).
