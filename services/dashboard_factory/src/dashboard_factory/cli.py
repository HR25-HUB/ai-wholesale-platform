from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from dashboard_factory import __version__
from dashboard_factory.evidence import build_metric_evidence, write_metric_evidence
from dashboard_factory.loaders import load_metric_definition, load_rfq_fixture
from dashboard_factory.metric_engine import MetricEngine

app = typer.Typer(no_args_is_help=True)


@app.command("verify-metric")
def verify_metric(
    dataset: Annotated[
        Path,
        typer.Option(exists=True, dir_okay=False, readable=True),
    ],
    contract: Annotated[
        Path,
        typer.Option(exists=True, dir_okay=False, readable=True),
    ],
    dataset_id: Annotated[str, typer.Option()],
    evidence_out: Annotated[Path, typer.Option(dir_okay=False)],
) -> None:
    """Calculate one versioned metric from a Golden RFQ fixture and write evidence JSON."""
    rows = load_rfq_fixture(dataset)
    definition = load_metric_definition(contract)
    result = MetricEngine().calculate(rows, definition)
    evidence = build_metric_evidence(
        dataset_id=dataset_id,
        result=result,
        engine_version=__version__,
    )
    write_metric_evidence(evidence_out, evidence)

    typer.echo(f"metric={result.metric_id}")
    typer.echo(f"version={result.metric_version}")
    typer.echo(f"numerator={result.numerator}")
    typer.echo(f"denominator={result.denominator}")
    typer.echo(f"value={result.value}")
    typer.echo(f"status={evidence.status}")
    typer.echo(f"evidence={evidence_out}")


if __name__ == "__main__":
    app()
