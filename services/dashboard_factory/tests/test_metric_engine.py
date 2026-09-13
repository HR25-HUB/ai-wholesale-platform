from datetime import UTC, datetime
from decimal import Decimal

from dashboard_factory.metric_engine import MetricEngine
from dashboard_factory.models import Condition, FilterSpec, MetricDefinition, RFQLine


def _line(line_id: str, *, offered: bool, ordered: bool) -> RFQLine:
    received = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)
    return RFQLine(
        rfq_id=f"RFQ-{line_id}",
        line_id=line_id,
        customer_id="C-1",
        manager_id="M-1",
        requested_mpn="ABB-S203-C16",
        requested_qty=Decimal("1"),
        received_at=received,
        offer_sent_at=(datetime(2026, 9, 13, 9, 0, tzinfo=UTC) if offered else None),
        order_confirmed=ordered,
        status="won" if ordered else "open",
    )


def test_rfq_offer_conversion_returns_verified_numerator_denominator_and_value() -> None:
    definition = MetricDefinition(
        metric_id="rfq_offer_conversion",
        version="1.0.0",
        name="RFQ Offer Conversion",
        grain="rfq",
        unit="ratio",
        denominator=FilterSpec(
            all=(Condition(field="offer_sent_at", operator="is_not_null"),)
        ),
        numerator=FilterSpec(
            all=(Condition(field="order_confirmed", operator="equals", value=True),)
        ),
    )
    dataset = [
        _line("1", offered=True, ordered=True),
        _line("2", offered=True, ordered=False),
        _line("3", offered=False, ordered=False),
    ]

    result = MetricEngine().calculate(dataset, definition)

    assert result.numerator == 1
    assert result.denominator == 2
    assert result.value == Decimal("0.5")


def test_numerator_never_exceeds_denominator_for_conversion_metric() -> None:
    definition = MetricDefinition(
        metric_id="rfq_offer_conversion",
        version="1.0.0",
        name="RFQ Offer Conversion",
        grain="rfq",
        unit="ratio",
        denominator=FilterSpec(
            all=(Condition(field="offer_sent_at", operator="is_not_null"),)
        ),
        numerator=FilterSpec(
            all=(Condition(field="order_confirmed", operator="equals", value=True),)
        ),
    )
    result = MetricEngine().calculate(
        [_line("1", offered=True, ordered=True), _line("2", offered=True, ordered=True)],
        definition,
    )

    assert result.numerator <= result.denominator
    assert Decimal("0") <= result.value <= Decimal("1")
