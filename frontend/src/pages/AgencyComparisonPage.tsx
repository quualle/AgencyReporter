import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

interface KpiItem {
  agency_id: string;
  agency_name: string;
  start_rate: number;
  completion_rate: number;
  early_end_rate: number;
}

interface ProblemItem {
  agency_id: string;
  problematic_percentage: number;
  cancelled_percentage: number;
  shortened_percentage: number;
}

const AgencyComparisonPage: React.FC = () => {
  const { timePeriod } = useAppStore();

  const [kpiData, setKpiData] = useState<KpiItem[]>([]);
  const [problemData, setProblemData] = useState<ProblemItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const [kpis, probs] = await Promise.all([
          apiService.getAllAgenciesQuotas(timePeriod),
          apiService.getProblematicStaysOverview(undefined, timePeriod)
        ]);

        setKpiData(kpis || []);
        setProblemData(probs?.data || []);
      } catch (err) {
        console.error('Error fetching comparison data:', err);
        setError('Fehler beim Laden der Daten.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [timePeriod]);

  if (isLoading) {
    return <Loading message="Vergleichsdaten werden geladen..." />;
  }

  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }

  const mergeData = () => {
    return kpiData.map(kpi => {
      const prob = problemData.find(p => p.agency_id === kpi.agency_id);
      return {
        ...kpi,
        problematic_percentage: prob?.problematic_percentage ?? null
      };
    });
  };

  const merged = mergeData();

  const sortBy = (key: keyof typeof merged[0], desc = true) => {
    return [...merged].sort((a: any, b: any) => {
      const va = a[key] ?? 0;
      const vb = b[key] ?? 0;
      return desc ? vb - va : va - vb;
    });
  };

  const top = (arr: any[], key: string, n = 5) => sortBy(key as any, true).slice(0, n);
  const flop = (arr: any[], key: string, n = 5) => sortBy(key as any, false).slice(0, n);

  const renderList = (items: any[], metric: string) => (
    <table className="min-w-full mb-6 text-sm">
      <thead>
        <tr>
          <th className="text-left p-2">Agentur</th>
          <th className="text-right p-2">{metric}</th>
        </tr>
      </thead>
      <tbody>
        {items.map((it, idx) => (
          <tr key={it.agency_id} className={idx % 2 ? 'bg-gray-50 dark:bg-gray-800' : ''}>
            <td className="p-2">{it.agency_name}</td>
            <td className="p-2 text-right">{(it[metric] * 100).toFixed(1)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Großer Agenturvergleich</h1>
      <p className="text-gray-600 dark:text-gray-300 mb-6">Top und Flop Listen der wichtigsten KPIs</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Top 5 Start-Rate</h2>
          {renderList(top(merged, 'start_rate'), 'start_rate')}
          <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Flop 5 Start-Rate</h2>
          {renderList(flop(merged, 'start_rate'), 'start_rate')}
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Top 5 Problemquote</h2>
          {renderList(top(merged, 'problematic_percentage'), 'problematic_percentage')}
          <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Flop 5 Problemquote</h2>
          {renderList(flop(merged, 'problematic_percentage'), 'problematic_percentage')}
        </div>
      </div>
    </div>
  );
};

export default AgencyComparisonPage;
