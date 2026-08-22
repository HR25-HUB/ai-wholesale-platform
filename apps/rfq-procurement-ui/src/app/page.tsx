import { evaluateRFQ } from "@/features/procurement/domain/decision-engine";
import { buildSyntheticRFQ } from "@/features/procurement/domain/synthetic-rfq";

function pct(value: number): string {
  return `${value.toFixed(1)}%`;
}

export default function HomePage() {
  const rfq = buildSyntheticRFQ(100);
  const { decisions, summary } = evaluateRFQ(rfq);
  const attention = decisions.filter((item) => item.status !== "READY");

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">PROCUREMENT CONTROL PLANE</p>
          <h1>{rfq.id}</h1>
          <p>{rfq.customerName} · {summary.totalLines} строк · {rfq.suppliers.length} поставщиков</p>
        </div>
        <span className="mode">SYNTHETIC / READ ONLY</span>
      </header>

      <section className="metrics" aria-label="Сводка RFQ">
        <article><span>Ready</span><strong>{summary.readyLines}</strong></article>
        <article><span>Review</span><strong>{summary.reviewLines}</strong></article>
        <article><span>Blocked</span><strong>{summary.blockedLines}</strong></article>
        <article><span>Quote coverage</span><strong>{pct(summary.quoteCoveragePct)}</strong></article>
        <article><span>Selected purchase cost</span><strong>€{summary.estimatedPurchaseCost.amount.toLocaleString("en-US", { maximumFractionDigits: 0 })}</strong></article>
      </section>

      <section className="panel">
        <div className="panelTitle">
          <div>
            <p className="eyebrow">EXCEPTION FIRST</p>
            <h2>Требуют внимания: {attention.length}</h2>
          </div>
          <p>Система не выполняет закупку автоматически. REVIEW / BLOCK требуют решения человека.</p>
        </div>

        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>Строка</th><th>Товар</th><th>Qty</th><th>Рекомендация</th><th>Confidence</th><th>Статус</th><th>Причина</th>
              </tr>
            </thead>
            <tbody>
              {attention.slice(0, 30).map((decision) => {
                const line = rfq.lines.find((item) => item.id === decision.lineId)!;
                const supplier = rfq.suppliers.find((item) => item.id === decision.recommendedSupplierId);
                return (
                  <tr key={decision.lineId}>
                    <td>{line.position}</td>
                    <td><strong>{line.requested.manufacturer} {line.requested.mpn}</strong><small>{line.requested.description}</small></td>
                    <td>{line.requested.quantity} {line.requested.unit}</td>
                    <td>{supplier?.name ?? "—"}</td>
                    <td>{pct(decision.decisionConfidence * 100)}</td>
                    <td><span className={`status ${decision.status.toLowerCase()}`}>{decision.disposition}</span></td>
                    <td>{decision.violations[0]?.message ?? decision.reasons[0]}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="panelTitle"><div><p className="eyebrow">DECISION MATRIX</p><h2>Первые 20 строк</h2></div></div>
        <div className="tableWrap">
          <table>
            <thead><tr><th>#</th><th>Запрошено</th>{rfq.suppliers.map((s) => <th key={s.id}>{s.id}</th>)}<th>Результат</th></tr></thead>
            <tbody>
              {rfq.lines.slice(0, 20).map((line) => {
                const decision = decisions.find((item) => item.lineId === line.id)!;
                return <tr key={line.id}>
                  <td>{line.position}</td>
                  <td><strong>{line.requested.mpn}</strong><small>{line.requested.quantity} {line.requested.unit}</small></td>
                  {rfq.suppliers.map((supplier) => {
                    const quote = line.quotes.find((item) => item.supplierId === supplier.id);
                    return <td key={supplier.id}>{quote ? <><strong>€{quote.unitPrice.amount.toFixed(2)}</strong><small>{quote.availableQuantity}/{line.requested.quantity} · {quote.deliveryDays}d</small></> : "—"}</td>;
                  })}
                  <td><strong>{decision.recommendedSupplierId ?? "No decision"}</strong><small>{decision.disposition}</small></td>
                </tr>;
              })}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
