from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from dashboard_factory.models import MetricDefinition


class MetricContractError(ValueError):
    """Raised when a metric contract cannot be parsed or validated."""


def load_metric_definition(path: Path) -> MetricDefinition:
    try:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise MetricContractError(f"Cannot load metric contract: {path}") from exc

    if not isinstance(raw, dict):
        raise MetricContractError("Metric contract root must be a mapping")

    try:
        return MetricDefinition.model_validate(raw)
    except ValidationError as exc:
        raise MetricContractError(f"Invalid metric contract: {path}") from exc
