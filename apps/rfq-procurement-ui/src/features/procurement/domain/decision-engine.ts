import type {
  ProcurementSummary,
  QuoteEvaluation,
  RFQ,
  RFQLine,
  RFQLineDecision,
  SupplierProfile,
  SupplierQuoteLine,
} from "./contracts";

const TODAY = new Date("2026-08-22T00:00:00Z");

function supplierFor(rfq: RFQ, supplierId: string): SupplierProfile {
  const supplier = rfq.suppliers.find((item) => item.id === supplierId);
  if (!supplier) throw new Error(`Unknown supplier: ${supplierId}`);
  return supplier;
}

function normalizedPrice(quote: SupplierQuoteLine): number {
  if (quote.unitPrice.currency !== "EUR") {
    throw new Error(`Unsupported benchmark currency: ${quote.unitPrice.currency}`);
  }
  return quote.unitPrice.amount;
}

export function evaluateQuote(rfq: RFQ, line: RFQLine, quote: SupplierQuoteLine): QuoteEvaluation {
  const supplier = supplierFor(rfq, quote.supplierId);
  const violations: QuoteEvaluation["violations"] = [];
  const reasons: string[] = [];

  if (new Date(quote.validUntil) < TODAY) {
    violations.push({ code: "QUOTE_EXPIRED", message: "Quotation is expired", severity: "CRITICAL" });
  }
  if (quote.availableQuantity < line.requested.quantity) {
    violations.push({ code: "PARTIAL_AVAILABILITY", message: "Supplier cannot cover requested quantity", severity: "WARNING" });
  }
  if (quote.identityConfidence < 0.75) {
    violations.push({ code: "LOW_IDENTITY_CONFIDENCE", message: "Product identity confidence is below review threshold", severity: "CRITICAL" });
  }
  if (quote.isSubstitution) {
    violations.push({ code: "SUBSTITUTION", message: "Supplier proposes a substitute product", severity: "WARNING" });
  }

  const eligible = !violations.some((item) => item.severity === "CRITICAL") && quote.availableQuantity >= line.requested.quantity;
  const price = normalizedPrice(quote);
  const priceScore = 1 / Math.max(price, 0.01);
  const deliveryScore = 1 / Math.max(quote.deliveryDays, 1);
  const score = priceScore * 0.45 + deliveryScore * 0.15 + supplier.reliability * 0.25 + quote.identityConfidence * 0.15;

  reasons.push(`price €${price.toFixed(2)}`);
  reasons.push(`delivery ${quote.deliveryDays}d`);
  reasons.push(`supplier reliability ${(supplier.reliability * 100).toFixed(0)}%`);
  reasons.push(`identity ${(quote.identityConfidence * 100).toFixed(0)}%`);

  return { quote, eligible, score, reasons, violations };
}

export function decideLine(rfq: RFQ, line: RFQLine): RFQLineDecision {
  if (line.identity.confidence < 0.75) {
    return {
      lineId: line.id,
      status: "BLOCKED",
      disposition: "BLOCK",
      decisionConfidence: line.identity.confidence,
      reasons: ["RFQ product identity requires manual resolution"],
      violations: [{ code: "RFQ_IDENTITY_LOW", message: "Requested product identity confidence is too low", severity: "CRITICAL" }],
    };
  }

  const evaluations = line.quotes.map((quote) => evaluateQuote(rfq, line, quote));
  const eligible = evaluations.filter((item) => item.eligible).sort((a, b) => b.score - a.score);
  const allViolations = evaluations.flatMap((item) => item.violations);

  if (eligible.length === 0) {
    return {
      lineId: line.id,
      status: "BLOCKED",
      disposition: line.quotes.length === 0 ? "ABSTAIN" : "BLOCK",
      decisionConfidence: 0,
      reasons: [line.quotes.length === 0 ? "No supplier quotations" : "No eligible supplier quotation"],
      violations: allViolations,
    };
  }

  const winner = eligible[0];
  const confidence = Math.min(0.99, Math.max(0.5, line.identity.confidence * supplierFor(rfq, winner.quote.supplierId).reliability));
  const needsReview = winner.quote.isSubstitution || confidence < 0.9 || eligible.length === 1;

  return {
    lineId: line.id,
    selectedSupplierId: needsReview ? undefined : winner.quote.supplierId,
    selectedQuoteId: needsReview ? undefined : winner.quote.id,
    recommendedSupplierId: winner.quote.supplierId,
    status: needsReview ? "REVIEW_REQUIRED" : "READY",
    disposition: needsReview ? "REVIEW" : "DECIDE",
    decisionConfidence: confidence,
    reasons: winner.reasons,
    violations: winner.violations,
  };
}

export function evaluateRFQ(rfq: RFQ): { decisions: RFQLineDecision[]; summary: ProcurementSummary } {
  const decisions = rfq.lines.map((line) => decideLine(rfq, line));
  let purchaseCost = 0;
  let quoted = 0;

  for (const line of rfq.lines) {
    if (line.quotes.length > 0) quoted += 1;
    const decision = decisions.find((item) => item.lineId === line.id);
    if (!decision?.selectedQuoteId) continue;
    const quote = line.quotes.find((item) => item.id === decision.selectedQuoteId);
    if (quote) purchaseCost += normalizedPrice(quote) * line.requested.quantity;
  }

  return {
    decisions,
    summary: {
      totalLines: rfq.lines.length,
      readyLines: decisions.filter((item) => item.status === "READY").length,
      reviewLines: decisions.filter((item) => item.status === "REVIEW_REQUIRED").length,
      blockedLines: decisions.filter((item) => item.status === "BLOCKED").length,
      quoteCoveragePct: rfq.lines.length === 0 ? 0 : (quoted / rfq.lines.length) * 100,
      estimatedPurchaseCost: { amount: purchaseCost, currency: "EUR" },
    },
  };
}
