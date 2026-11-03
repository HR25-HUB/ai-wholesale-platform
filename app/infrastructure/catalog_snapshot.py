"""Explicit, read-only catalog snapshot. Never infers production PIM availability."""
import json
from pathlib import Path

from contracts.product_matching import ProductCatalogRecord


class JsonCatalogSnapshot:
    """A deliberately small, authorized export for the initial vertical slice."""

    def __init__(self, path: str):
        self._path = Path(path)

    def find_by_part_number(self, part_number: str) -> list[ProductCatalogRecord]:
        # Avoid accidentally reading and returning secrets from arbitrary file locations:
        # deployment operator must explicitly supply and approve this snapshot path.
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("catalog snapshot must be a JSON array")
        records = [ProductCatalogRecord.model_validate(item) for item in data]
        needle = " ".join(part_number.strip().casefold().split())
        return [
            record
            for record in records
            if " ".join(record.part_number.strip().casefold().split()) == needle
        ]
