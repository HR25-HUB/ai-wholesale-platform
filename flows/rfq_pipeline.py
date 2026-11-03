"""One RFQ line -> read-only catalog matching; runnable with a local Prefect engine."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from prefect import flow, task

from app.application.product_matching import MatchRFQLine
from app.infrastructure.catalog_snapshot import JsonCatalogSnapshot
from contracts.product_matching import ProductMatchResult, RFQLineInput


@task(name="match-rfq-line", retries=0)
def match_line(
    line: RFQLineInput, catalog_snapshot_path: str, correlation_id: str
) -> ProductMatchResult:
    # Compose adapters in the worker, not in serialized deployment parameters.
    service = MatchRFQLine(JsonCatalogSnapshot(catalog_snapshot_path))
    return service.execute(line, correlation_id)


@flow(name="NUIF-PREFECT-001.A1.1", log_prints=False)
def rfq_pipeline(
    line: RFQLineInput, catalog_snapshot_path: str, correlation_id: str | None = None
) -> ProductMatchResult:
    if not catalog_snapshot_path.strip():
        raise ValueError("an explicitly approved read-only catalog snapshot is required")
    return match_line(line, catalog_snapshot_path, correlation_id or str(uuid4()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read-only RFQ matching slice")
    parser.add_argument("--rfq-line", required=True, help="Path to authorized RFQLineInput JSON")
    parser.add_argument("--catalog", required=True, help="Path to authorized PIM export JSON")
    args = parser.parse_args()
    rfq_line = RFQLineInput.model_validate_json(
        Path(args.rfq_line).read_text(encoding="utf-8")
    )
    # CLI output is not a durable business audit.
    print(json.dumps(rfq_pipeline(rfq_line, args.catalog).model_dump(mode="json"), indent=2))
