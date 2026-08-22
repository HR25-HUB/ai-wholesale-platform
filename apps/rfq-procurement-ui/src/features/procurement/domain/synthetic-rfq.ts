import type { RFQ, RFQLine, SupplierProfile, SupplierQuoteLine } from "./contracts";

const suppliers: SupplierProfile[] = [
  { id: "SUP-A", name: "Alpha Electric", reliability: 0.96, averageDeliveryDays: 3 },
  { id: "SUP-B", name: "Baltic Components", reliability: 0.88, averageDeliveryDays: 8 },
  { id: "SUP-C", name: "Central Automation", reliability: 0.98, averageDeliveryDays: 2 },
  { id: "SUP-D", name: "Delta Industrial", reliability: 0.82, averageDeliveryDays: 5 },
  { id: "SUP-E", name: "EuroTech Supply", reliability: 0.93, averageDeliveryDays: 4 },
];

const products = [
  ["ABB", "AF09-30-10", "ABB AF09 contactor"],
  ["Siemens", "3RT2016", "Siemens SIRIUS contactor"],
  ["Schneider", "LC1D09", "Schneider TeSys contactor"],
  ["WAGO", "221-413", "WAGO connector"],
  ["Phoenix Contact", "PT 2,5", "Phoenix Contact terminal"],
] as const;

function pseudo(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

function quote(lineNo: number, supplier: SupplierProfile, basePrice: number, quantity: number): SupplierQuoteLine {
  const index = suppliers.findIndex((item) => item.id === supplier.id);
  const noise = 0.9 + pseudo(lineNo * 17 + index * 31) * 0.22;
  const scenario = lineNo % 20;
  const availableQuantity = scenario === 7 && index === 0 ? Math.max(1, Math.floor(quantity * 0.4)) : quantity;
  const expired = scenario === 11 && index === 1;
  const substitution = scenario === 13 && index === 2;
  const identityConfidence = scenario === 17 && index === 3 ? 0.68 : substitution ? 0.82 : 0.96;

  return {
    id: `Q-${lineNo}-${supplier.id}`,
    supplierId: supplier.id,
    unitPrice: { amount: Number((basePrice * noise).toFixed(2)), currency: "EUR" },
    availableQuantity,
    deliveryDays: Math.max(1, supplier.averageDeliveryDays + Math.floor(pseudo(lineNo + index) * 3) - 1),
    validUntil: expired ? "2026-08-20" : "2026-09-30",
    identityConfidence,
    isSubstitution: substitution,
  };
}

export function buildSyntheticRFQ(lineCount = 100): RFQ {
  const lines: RFQLine[] = Array.from({ length: lineCount }, (_, index) => {
    const position = index + 1;
    const product = products[index % products.length];
    const quantity = 10 + (index % 9) * 10;
    const noQuotes = position % 23 === 0;
    const lowIdentity = position % 29 === 0;
    const basePrice = 8 + (index % 17) * 4.2;

    return {
      id: `LINE-${position.toString().padStart(3, "0")}`,
      position,
      requested: {
        manufacturer: product[0],
        mpn: product[1],
        description: product[2],
        quantity,
        unit: "pcs",
      },
      identity: {
        confidence: lowIdentity ? 0.64 : 0.97,
        status: lowIdentity ? "AMBIGUOUS" : "MATCHED",
      },
      quotes: noQuotes ? [] : suppliers.map((supplier) => quote(position, supplier, basePrice, quantity)),
    };
  });

  return {
    id: "RFQ-SYN-PROD-001",
    customerName: "Synthetic Industrial Customer",
    createdAt: "2026-08-22T09:00:00Z",
    currency: "EUR",
    suppliers,
    lines,
  };
}
