"""Objects module providing base classes for table and column information.

This module exports the core data classes used for representing SQL
table and column metadata.
"""

from .generic import Unknown, is_undetermined, unknown
from .info_objects import SQLColumnInfoBase, SQLTableInfoBase

__all__ = [
    "SQLColumnInfoBase",
    "SQLTableInfoBase",
    "Unknown",
    "is_undetermined",
    "unknown",
]
