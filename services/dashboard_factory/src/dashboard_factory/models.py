from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RFQLine(BaseModel):
    """Canonical RFQ line used by the Dashboard Factory vertical slice."""

    model_config = ConfigDict(frozen=True)

    rfq_id: str
    line_id: str
    customer_id: str
    manager_id: str
    requested_mpn: str
    requested_qty: Decimal = Field(gt=0)
    matched_product_id: str | None = None
    supplier_id: str | None = None
    supplier_price: Decimal | None = Field(default=None, ge=0)
    offer_price: Decimal | None = Field(default=None, ge=0)
    received_at: datetime
    offer_sent_at: datetime | None = None
    order_confirmed: bool = False
    status: str


class Condition(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    operator: Literal[
        "equals",
        "not_equals",
        "is_null",
        "is_not_null",
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal",
        "in",
    ]
    value: object | None = None


class FilterSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    all: tuple[Condition, ...] = ()


class MetricDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric_id: str
    version: str
    name: str
    grain: Literal["rfq", "rfq_line"]
    numerator: FilterSpec
    denominator: FilterSpec
    unit: Literal["ratio", "count", "seconds", "currency"]


class MetricResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric_id: str
    metric_version: str
    value: Decimal
    numerator: int | None = None
    denominator: int | None = None


class MetricSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    dataset_id: str
    metric: MetricResult
    calculated_at: datetime
    status: Literal["VERIFIED", "REVIEW_REQUIRED", "REJECTED"]
