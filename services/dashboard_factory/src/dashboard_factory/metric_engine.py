from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from operator import eq, ge, gt, le, lt, ne

from dashboard_factory.models import Condition, FilterSpec, MetricDefinition, MetricResult, RFQLine


class MetricUndefinedError(ValueError):
    pass


class UnsupportedConditionError(ValueError):
    pass


class MetricEngine:
    """Deterministic metric evaluation over canonical RFQ lines."""

    def calculate(self, dataset: Iterable[RFQLine], definition: MetricDefinition) -> MetricResult:
        rows = list(dataset)
        denominator_rows = self._apply_filter(rows, definition.denominator)
        numerator_rows = self._apply_filter(denominator_rows, definition.numerator)

        denominator = self._count_at_grain(denominator_rows, definition.grain)
        numerator = self._count_at_grain(numerator_rows, definition.grain)

        if definition.unit == "count":
            return MetricResult(
                metric_id=definition.metric_id,
                metric_version=definition.version,
                value=Decimal(numerator),
                numerator=numerator,
                denominator=None,
            )

        if denominator == 0:
            raise MetricUndefinedError(definition.metric_id)

        value = Decimal(numerator) / Decimal(denominator)
        return MetricResult(
            metric_id=definition.metric_id,
            metric_version=definition.version,
            value=value,
            numerator=numerator,
            denominator=denominator,
        )

    def _count_at_grain(self, rows: list[RFQLine], grain: str) -> int:
        if grain == "rfq_line":
            return len(rows)
        if grain == "rfq":
            return len({row.rfq_id for row in rows})
        raise UnsupportedConditionError(f"Unsupported metric grain: {grain}")

    def _apply_filter(self, rows: list[RFQLine], spec: FilterSpec) -> list[RFQLine]:
        return [row for row in rows if all(self._matches(row, c) for c in spec.all)]

    def _matches(self, row: RFQLine, condition: Condition) -> bool:
        if not hasattr(row, condition.field):
            raise UnsupportedConditionError(f"Unknown field: {condition.field}")

        actual = getattr(row, condition.field)
        op = condition.operator
        expected = condition.value

        if op == "is_null":
            return actual is None
        if op == "is_not_null":
            return actual is not None
        if op == "in":
            if not isinstance(expected, (list, tuple, set, frozenset)):
                raise UnsupportedConditionError("'in' requires a collection value")
            return actual in expected

        comparators = {
            "equals": eq,
            "not_equals": ne,
            "greater_than": gt,
            "less_than": lt,
        }
        if op in comparators:
            return comparators[op](actual, expected)

        if op == "greater_than_or_equal":
            return ge(actual, expected)
        if op == "less_than_or_equal":
            return le(actual, expected)

        raise UnsupportedConditionError(f"Unsupported operator: {op}")
