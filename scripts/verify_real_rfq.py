"""Operator-controlled real-case execution; no live PIM or commercial mutations."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from app.application.evidence_verification import (
    load_and_validate_case,
    verify_result,
)
from flows.rfq_pipeline import rfq_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run approved real RFQLine through Prefect")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rfq", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest, line = load_and_validate_case(args.manifest, args.rfq, args.catalog)
    correlation_id = str(uuid4())
    result = rfq_pipeline(line, str(args.catalog), correlation_id)
    outcome = verify_result(manifest, result)
    if args.output.exists():
        raise FileExistsError("refusing to overwrite an existing evidence bundle")
    # Prevent accidental inclusion of raw RFQ input/PII: write only approved metadata.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as fp:
        json.dump(outcome.model_dump(mode="json"), fp, indent=2)
    print(f"Evidence bundle created: {args.output} (correlation_id={correlation_id})")


if __name__ == "__main__":
    main()
