import React, { useEffect, useState } from 'react';
import AgencySelector from '../components/common/AgencySelector';
import { useAppStore } from '../store/appStore';
import Loading from '../components/common/Loading';
import ExportButton from '../components/common/ExportButton';

// Typen für die wichtigsten Daten (vereinfachtes MVP)
type Kpis = {
  deployments?: number;
  abort_rate?: number;
  churn_30d?: number;
  [key: string]: any;
};

type Comparison = {
  selected_agency?: any;
  industry_average?: any;
};

type Reasons = Record<string, number>;

const AgencyReportPage: React.FC = () => {
  const { selectedAgency } = useAppStore();
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [reasons, setReasons] = useState<Reasons | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      setLoading(true);
      try {
        const [kpisRes, comparisonRes, reasonsRes] = await Promise.all([
          fetch(`/api/quotas/${selectedAgency.agency_id}/all`).then(r => r.json()),
          fetch(`/api/reaction_times/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agency_id: selectedAgency.agency_id, time_period: 'last_quarter' })
          }).then(r => r.json()),
          fetch(`/api/quotas_with_reasons/${selectedAgency.agency_id}/early-end-reasons`).then(r => r.json())
        ]);
        setKpis(kpisRes);
        setComparison(comparisonRes);
        setReasons(reasonsRes.early_end_reasons || {});
      } catch (e) {
        setKpis(null);
        setComparison(null);
        setReasons(null);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedAgency]);

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Agentur-Report</h1>
      <AgencySelector />
      {!selectedAgency && <div className="mt-8">Bitte wähle eine Agentur aus.</div>}
      {loading && <Loading />}
      {selectedAgency && !loading && (
        <>
          <div id="report-content">
            <section className="my-6">
              <h2 className="text-xl font-semibold mb-2">KPIs</h2>
              <div className="flex gap-4 flex-wrap">
                <KpiTile label="Deployments" value={kpis?.deployments} />
                <KpiTile label="Abbrüche (%)" value={kpis?.abort_rate} />
                <KpiTile label="Churn (30d)" value={kpis?.churn_30d} />
                {/* Weitere KPIs nach Bedarf */}
              </div>
            </section>
            <section className="my-6">
              <h2 className="text-xl font-semibold mb-2">Vergleich mit Branchendurchschnitt</h2>
              <ComparisonSection comparison={comparison} />
            </section>
            <section className="my-6">
              <h2 className="text-xl font-semibold mb-2">Gründe für Abbrüche / Beendigungen</h2>
              <ReasonTable reasons={reasons} />
            </section>
          </div>
          <section className="my-6">
            <ExportButton targetElementId="report-content" filename="agentur-report" pageTitle="Agentur-Report" />
          </section>
        </>
      )}
    </div>
  );
};

const KpiTile: React.FC<{ label: string; value: any }> = ({ label, value }) => (
  <div className="border rounded p-4 min-w-[120px] text-center bg-white dark:bg-gray-800 shadow">
    <div className="font-semibold text-gray-700 dark:text-gray-200">{label}</div>
    <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{value ?? '–'}</div>
  </div>
);

const ComparisonSection: React.FC<{ comparison: Comparison | null }> = ({ comparison }) => {
  if (!comparison) return <div>Keine Vergleichsdaten verfügbar.</div>;
  // MVP: Nur ein paar Werte als Text, später als Chart
  return (
    <div className="flex gap-8">
      <div>
        <div className="font-semibold">Agentur</div>
        <div>{JSON.stringify(comparison.selected_agency)}</div>
      </div>
      <div>
        <div className="font-semibold">Branchendurchschnitt</div>
        <div>{JSON.stringify(comparison.industry_average)}</div>
      </div>
    </div>
  );
};

const ReasonTable: React.FC<{ reasons: Reasons | null }> = ({ reasons }) => {
  if (!reasons || Object.keys(reasons).length === 0) return <div>Keine Gründe vorhanden.</div>;
  return (
    <table className="min-w-[300px] border mt-2">
      <thead>
        <tr>
          <th className="border px-2 py-1">Grund</th>
          <th className="border px-2 py-1">Anzahl</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(reasons).map(([reason, count]) => (
          <tr key={reason}>
            <td className="border px-2 py-1">{reason}</td>
            <td className="border px-2 py-1">{count}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AgencyReportPage; 