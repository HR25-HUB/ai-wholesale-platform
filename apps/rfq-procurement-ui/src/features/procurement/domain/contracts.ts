export type Currency = "EUR" | "USD" | "RUB";
export type DecisionDisposition = "DECIDE" | "REVIEW" | "ABSTAIN" | "BLOCK";
export type LineStatus = "READY" | "REVIEW_REQUIRED" | "BLOCKED" | "APPROVED";
export type PolicySeverity = "INFO" | "WARNING" | "CRITICAL";

export interface Money {
  amount: number;
  currency: Currency;
}

export interface SupplierProfile {
  id: string;
  name: string;
  reliability: number;
  averageDeliveryDays: number;
}

export interface SupplierQuoteLine {
  id: string;
  supplierId: string;
  unitPrice: Money;
  availableQuantity: number;
  deliveryDays: number;
  validUntil: string;
  identityConfidence: number;
  isSubstitution: boolean;
}

export interface RFQLine {
  id: string;
  position: number;
  requested: {
    description: string;
    manufacturer?: string;
    mpn?: string;
    quantity: number;
    unit: "pcs" | "m" | "set";
  };
  identity: {
    confidence: number;
    status: "MATCHED" | "AMBIGUOUS" | "SUBSTITUTION" | "NOT_FOUND";
  };
  quotes: SupplierQuoteLine[];
}

export interface RFQ {
  id: string;
  customerName: string;
  createdAt: string;
  currency: Currency;
  lines: RFQLine[];
  suppliers: SupplierProfile[];
}

export interface PolicyViolation {
  code: string;
  message: string;
  severity: PolicySeverity;
}

export interface QuoteEvaluation {
  quote: SupplierQuoteLine;
  eligible: boolean;
  score: number;
  reasons: string[];
  violations: PolicyViolation[];
}

export interface RFQLineDecision {
  lineId: string;
  selectedSupplierId?: string;
  selectedQuoteId?: string;
  recommendedSupplierId?: string;
  status: LineStatus;
  disposition: DecisionDisposition;
  decisionConfidence: number;
  reasons: string[];
  violations: PolicyViolation[];
}

export interface ProcurementSummary {
  totalLines: number;
  readyLines: number;
  reviewLines: number;
  blockedLines: number;
  quoteCoveragePct: number;
  estimatedPurchaseCost: Money;
}
