from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from dashboard_factory.models import MetricResult


class MetricEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_id: str
    metric_id: str
    metric_version: str
    engine_version: str
    calculated_at: datetime
    result: MetricResult
    status: str


def build_metric_evidence(
    *,
    dataset_id: str,
    result: MetricResult,
    engine_version: str,
    status: str = "VERIFIED",
) -> MetricEvidence:
    return MetricEvidence(
        dataset_id=dataset_id,
        metric_id=result.metric_id,
        metric_version=result.metric_version,
        engine_version=engine_version,
        calculated_at=datetime.now(UTC),
        result=result,
        status=status,
    )


def write_metric_evidence(path: Path, evidence: MetricEvidence) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = evidence.model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
