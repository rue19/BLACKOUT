"""
BLACKOUT ID Mapper - Maps string IDs to integer IDs for HydraDB
"""

import hashlib
from typing import Any


class IDMapper:
    """Maps string IDs to non-negative integer IDs for HydraDB."""

    def __init__(self):
        self.string_to_int: dict[str, int] = {}
        self.int_to_string: dict[int, str] = {}
        self._counter = 1  # Start from 1

    def get_int_id(self, string_id: str) -> int:
        """Get or create integer ID for a string ID."""
        if string_id not in self.string_to_int:
            int_id = self._counter
            self._counter += 1
            self.string_to_int[string_id] = int_id
            self.int_to_string[int_id] = string_id
        return self.string_to_int[string_id]

    def get_string_id(self, int_id: int) -> str | None:
        """Get original string ID from integer ID."""
        return self.int_to_string.get(int_id)

    def has_id(self, string_id: str) -> bool:
        """Check if string ID has been mapped."""
        return string_id in self.string_to_int

    def batch_get_int_ids(self, string_ids: list[str]) -> list[dict[str, Any]]:
        """Convert a list of string IDs to int_id mappings for UNWIND."""
        return [{"string_id": sid, "int_id": self.get_int_id(sid)} for sid in string_ids]
