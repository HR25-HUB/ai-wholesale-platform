from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from dashboard_factory.models import MetricDefinition, RFQLine


class ContractLoadError(ValueError):
    """Raised when a versioned metric contract cannot be validated."""


class DatasetLoadError(ValueError):
    """Raised when a Golden dataset cannot be validated."""


def load_metric_definition(path: Path) -> MetricDefinition:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ContractLoadError(f"Metric contract must be a mapping: {path}")
        return MetricDefinition.model_validate(payload)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise ContractLoadError(f"Invalid metric contract: {path}") from exc


def load_rfq_fixture(path: Path) -> list[RFQLine]:
    rows: list[RFQLine] = []
    try:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
                rows.append(RFQLine.model_validate(payload))
            except (json.JSONDecodeError, ValidationError) as exc:
                raise DatasetLoadError(
                    f"Invalid Golden RFQ row at line {line_number}: {path}"
                ) from exc
    except OSError as exc:
        raise DatasetLoadError(f"Cannot read Golden RFQ fixture: {path}") from exc

    if not rows:
        raise DatasetLoadError(f"Golden RFQ fixture is empty: {path}")

    identities = {(row.rfq_id, row.line_id) for row in rows}
    if len(identities) != len(rows):
        raise DatasetLoadError("Golden RFQ fixture contains duplicate (rfq_id, line_id)")

    return rows
