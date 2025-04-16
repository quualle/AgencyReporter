import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface LLMAnalysisData {
  agency_id: string;
  analysis_type: string;
  reason_categories: Record<string, number>;
  total_analyzed: number;
}

interface SummaryData {
  agency_id: string;
  summary: string;
}

const COLORS = [
  '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#6366f1',
  '#0ea5e9', '#8b5cf6', '#ec4899', '#14b8a6', '#f43f5e',
  '#84cc16', '#6b7280', '#7c3aed', '#059669', '#d946ef'
];

// Define category name mapping
const CATEGORY_NAMES: Record<string, string> = {
  // Cancellation categories
  caregiver_unavailable: 'Betreuungskraft verhindert',
  health_issues: 'Gesundheitliche Probleme',
  customer_dissatisfied: 'Kunde unzufrieden',
  communication_problems: 'Kommunikationsprobleme',
  qualification_mismatch: 'Qualifikation passt nicht',
  pricing_issues: 'Preisprobleme',
  scheduling_conflict: 'Terminkonflikt',
  administrative_issues: 'Administrative Probleme',
  changed_requirements: 'Geänderte Anforderungen',
  family_issues: 'Familiäre Gründe',
  transport_issues: 'Transportprobleme',
  personal_conflict: 'Persönlicher Konflikt',
  better_offer: 'Besseres Angebot',
  accommodation_issues: 'Unterkunftsprobleme',
  other: 'Sonstiges',

  // Violation categories
  experience_misrepresentation: 'Erfahrung falsch dargestellt',
  language_skill_exaggeration: 'Sprachkenntnisse übertrieben',
  smoking_status_incorrect: 'Raucherstatus inkorrekt',
  age_discrepancy: 'Altersabweichung',
  license_issues: 'Führerschein-Probleme',
  qualification_misrepresentation: 'Qualifikation falsch dargestellt',
  false_availability: 'Falsche Verfügbarkeit',
  document_issues: 'Dokumentenprobleme',
  personality_mismatch: 'Persönlichkeitsdiskrepanz'
};

const LLMAnalysisPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [cancellationData, setCancellationData] = useState<LLMAnalysisData | null>(null);
  const [violationData, setViolationData] = useState<LLMAnalysisData | null>(null);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch data in parallel
        const [cancellationResponse, violationResponse, summaryResponse] = await Promise.all([
          apiService.getCancellationAnalysis(selectedAgency.agency_id, timePeriod),
          apiService.getViolationsAnalysis(selectedAgency.agency_id, timePeriod),
          apiService.getAgencySummary(selectedAgency.agency_id, timePeriod)
        ]);
        
        setCancellationData(cancellationResponse);
        setViolationData(violationResponse);
        setSummaryData(summaryResponse);
      } catch (err) {
        console.error('Error fetching LLM analysis data:', err);
        setError('Fehler beim Laden der LLM-Analyse-Daten. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const transformDataForChart = (data: LLMAnalysisData | null) => {
    if (!data || !data.reason_categories) return [];
    
    return Object.entries(data.reason_categories).map(([key, value]) => ({
      name: CATEGORY_NAMES[key] || key,
      value: value,
      id: key
    }));
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="text-xs font-medium"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  if (isLoading) {
    return <Loading message="LLM-Analyse wird geladen..." />;
  }

  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }

  if (!selectedAgency) {
    return (
      <div className="text-center p-8">
        <h2 className="text-xl font-semibold mb-4">Keine Agentur ausgewählt</h2>
        <p className="text-gray-600 dark:text-gray-300">Bitte wählen Sie eine Agentur aus dem Dropdown-Menü.</p>
      </div>
    );
  }

  return (
    <div className="llm-analysis-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
          LLM-Analyse: {selectedAgency.agency_name}
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          KI-gestützte Analyse der Abbruchgründe und Regelverstöße
        </p>
      </div>

      {/* AI Summary */}
      {summaryData && (
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">KI-generierte Zusammenfassung</h2>
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p className="text-gray-600 dark:text-gray-300 italic">
              {summaryData.summary}
            </p>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 text-right mt-2">
            * Generiert mit GPT-4
          </p>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Cancellation Analysis */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Abbruchgründe</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Analyse der häufigsten Gründe für Abbrüche von Reservierungen und Einsätzen.
            Basierend auf {cancellationData?.total_analyzed || 0} analysierten Kommunikationen.
          </p>
          
          {cancellationData && cancellationData.total_analyzed > 0 ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={transformDataForChart(cancellationData)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {transformDataForChart(cancellationData).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`${value} Fälle`, 'Anzahl']}
                    labelFormatter={(label) => `Grund: ${label}`}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">Keine Daten verfügbar</p>
            </div>
          )}
          
          <div className="mt-4">
            <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Top Abbruchgründe</h3>
            <div className="space-y-2">
              {transformDataForChart(cancellationData)
                .sort((a, b) => b.value - a.value)
                .slice(0, 5)
                .map((item, index) => (
                  <div key={index} className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                    <div className="flex-1 flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">{item.name}</span>
                      <span className="font-medium text-gray-800 dark:text-white">
                        {((item.value / (cancellationData?.total_analyzed || 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Violation Analysis */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Regelverstöße</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Analyse der Diskrepanzen zwischen Profilangaben und realer Wahrnehmung.
            Basierend auf {violationData?.total_analyzed || 0} analysierten Berichten.
          </p>
          
          {violationData && violationData.total_analyzed > 0 ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={transformDataForChart(violationData)}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    tick={{ fontSize: 12 }}
                    width={150}
                  />
                  <Tooltip 
                    formatter={(value: number) => [`${value} Fälle`, 'Anzahl']}
                    labelFormatter={(label) => `Regelverstoß: ${label}`}
                  />
                  <Bar dataKey="value" name="Anzahl">
                    {transformDataForChart(violationData).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">Keine Daten verfügbar</p>
            </div>
          )}
          
          <div className="mt-4">
            <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Top Regelverstöße</h3>
            <div className="space-y-2">
              {transformDataForChart(violationData)
                .sort((a, b) => b.value - a.value)
                .slice(0, 5)
                .map((item, index) => (
                  <div key={index} className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                    <div className="flex-1 flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-300">{item.name}</span>
                      <span className="font-medium text-gray-800 dark:text-white">
                        {((item.value / (violationData?.total_analyzed || 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Detaillierte Analyse</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Vollständige Aufschlüsselung aller Kategorien und deren Häufigkeit.
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Kategorie
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Typ
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Anzahl
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Prozent
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {[
                ...(transformDataForChart(cancellationData).map(item => ({ ...item, type: 'Abbruch' }))),
                ...(transformDataForChart(violationData).map(item => ({ ...item, type: 'Regelverstoß' })))
              ].map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {item.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {item.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {item.value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {((item.value / (item.type === 'Abbruch' ? (cancellationData?.total_analyzed || 1) : (violationData?.total_analyzed || 1))) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LLMAnalysisPage; 