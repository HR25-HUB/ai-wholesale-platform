import { describe, expect, it } from "vitest";
import { decideLine, evaluateRFQ } from "../src/features/procurement/domain/decision-engine";
import { buildSyntheticRFQ } from "../src/features/procurement/domain/synthetic-rfq";

describe("RFQ procurement decision engine", () => {
  it("processes the deterministic 100-line benchmark", () => {
    const rfq = buildSyntheticRFQ(100);
    const result = evaluateRFQ(rfq);

    expect(result.summary.totalLines).toBe(100);
    expect(result.summary.quoteCoveragePct).toBeGreaterThan(90);
    expect(result.decisions).toHaveLength(100);
    expect(result.decisions.some((item) => item.disposition === "BLOCK")).toBe(true);
    expect(result.decisions.some((item) => item.disposition === "REVIEW")).toBe(true);
  });

  it("abstains when a line has no quotes", () => {
    const rfq = buildSyntheticRFQ(23);
    const line = rfq.lines[22];
    const decision = decideLine(rfq, line);

    expect(line.quotes).toHaveLength(0);
    expect(decision.disposition).toBe("ABSTAIN");
    expect(decision.selectedSupplierId).toBeUndefined();
  });

  it("never auto-selects an expired quote", () => {
    const rfq = buildSyntheticRFQ(11);
    const line = rfq.lines[10];
    const decision = decideLine(rfq, line);
    const expired = line.quotes.find((quote) => quote.validUntil === "2026-08-20");

    expect(expired).toBeDefined();
    expect(decision.selectedQuoteId).not.toBe(expired?.id);
  });
});
