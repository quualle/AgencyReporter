import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService, { StrengthWeaknessAnalysis, StrengthWeaknessItem } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from 'recharts';

const StrengthWeaknessPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [analysisData, setAnalysisData] = useState<StrengthWeaknessAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await apiService.getStrengthWeaknessAnalysis(
          selectedAgency.agency_id, 
          timePeriod
        );
        
        setAnalysisData(response);
      } catch (err) {
        console.error('Error fetching strength/weakness data:', err);
        setError('Fehler beim Laden der Stärken-/Schwächenanalyse. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const getRadarData = () => {
    if (!analysisData) return [];
    
    // Combine strengths and weaknesses for radar chart
    const allMetrics = [...analysisData.strengths, ...analysisData.weaknesses, ...analysisData.neutral];
    
    return allMetrics.map(item => ({
      subject: item.metric_name,
      value: item.normalized_score,
      benchmark: 0.5, // Benchmark line at middle
    }));
  };

  const getStrengthsData = () => {
    if (!analysisData) return [];
    return [...analysisData.strengths].sort((a, b) => b.normalized_score - a.normalized_score);
  };
  
  const getWeaknessesData = () => {
    if (!analysisData) return [];
    return [...analysisData.weaknesses].sort((a, b) => a.normalized_score - b.normalized_score);
  };

  const getBarColor = (item: StrengthWeaknessItem) => {
    if (item.category === 'strength') return '#10b981';
    if (item.category === 'weakness') return '#ef4444';
    return '#9ca3af';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.75) return 'Hervorragend';
    if (score >= 0.60) return 'Überdurchschnittlich';
    if (score >= 0.45) return 'Durchschnittlich';
    if (score >= 0.30) return 'Unterdurchschnittlich';
    return 'Kritisch';
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.75) return 'text-green-500';
    if (score >= 0.60) return 'text-green-400';
    if (score >= 0.45) return 'text-yellow-500';
    if (score >= 0.30) return 'text-orange-500';
    return 'text-red-500';
  };

  if (isLoading) {
    return <Loading message="Stärken-/Schwächen-Analyse wird geladen..." />;
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
    <div className="strength-weakness-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
          Stärken/Schwächen: {selectedAgency.agency_name}
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Detaillierte Analyse der Stärken und Schwächen im Vergleich zum Branchendurchschnitt
        </p>
      </div>

      {/* Overall Score */}
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="mb-4 md:mb-0">
            <h2 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">Gesamtbewertung</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Die Gesamtbewertung basiert auf allen analysierten Metriken und berücksichtigt sowohl 
              Stärken als auch Schwächen dieser Agentur.
            </p>
          </div>
          
          <div className="flex flex-col items-center">
            <div 
              className="relative w-36 h-36 rounded-full flex items-center justify-center text-2xl font-bold"
              style={{
                background: `conic-gradient(
                  ${analysisData?.overall_score && analysisData.overall_score >= 0.6 ? '#10b981' : 
                    (analysisData?.overall_score && analysisData.overall_score <= 0.4 ? '#ef4444' : '#f59e0b')
                  } ${(analysisData?.overall_score || 0.5) * 360}deg,
                  #e5e7eb ${(analysisData?.overall_score || 0.5) * 360}deg 360deg
                )`
              }}
            >
              <div className="absolute inset-3 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-3xl font-bold text-gray-800 dark:text-white">
                    {Math.round((analysisData?.overall_score || 0) * 100)}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Punkte</div>
                </div>
              </div>
            </div>
            <p className={`mt-2 font-semibold ${getScoreColor(analysisData?.overall_score || 0)}`}>
              {getScoreLabel(analysisData?.overall_score || 0)}
            </p>
          </div>
        </div>
        
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-gray-600 dark:text-gray-300">Stärken</p>
              <p className="text-xl font-semibold text-green-500">
                {analysisData?.strengths.length || 0}
              </p>
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-300">Neutral</p>
              <p className="text-xl font-semibold text-gray-500">
                {analysisData?.neutral.length || 0}
              </p>
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-300">Schwächen</p>
              <p className="text-xl font-semibold text-red-500">
                {analysisData?.weaknesses.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Performance-Überblick</h2>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
          Radar-Diagramm der Agentur-Performance in allen Bereichen im Vergleich zum Branchendurchschnitt.
          Größere Flächen zeigen bessere Performance.
        </p>
        
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart outerRadius={130} data={getRadarData()}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 1]} tickCount={6} />
              <Radar
                name={selectedAgency.agency_name}
                dataKey="value"
                stroke="#4f46e5"
                fill="#4f46e5"
                fillOpacity={0.5}
              />
              <Radar
                name="Benchmark"
                dataKey="benchmark"
                stroke="#9ca3af"
                strokeDasharray="5 5"
                fill="none"
              />
              <Tooltip 
                formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Performance']}
                labelFormatter={(label) => `Metrik: ${label}`}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Strengths and Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Strengths */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Top Stärken</h2>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={getStrengthsData().slice(0, 5)}
                margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  domain={[0, 1]} 
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <YAxis 
                  type="category" 
                  dataKey="metric_name" 
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Score']}
                  labelFormatter={(label) => `Metrik: ${label}`}
                />
                <Bar dataKey="normalized_score" name="Performance">
                  {getStrengthsData().slice(0, 5).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill="#10b981" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4">
            <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Details</h3>
            <div className="space-y-3">
              {getStrengthsData().slice(0, 5).map((item, index) => (
                <div key={index} className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-800 dark:text-white">{item.metric_name}</span>
                    <span className="text-green-600 dark:text-green-400 font-semibold">
                      {item.value_formatted}
                    </span>
                  </div>
                  <div className="mt-1 flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Branchendurchschnitt: {item.benchmark_formatted}</span>
                    <span className="text-green-600 dark:text-green-400">
                      +{((item.value - item.benchmark) / item.benchmark * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Weaknesses */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Top Schwächen</h2>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={getWeaknessesData().slice(0, 5)}
                margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  domain={[0, 1]} 
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <YAxis 
                  type="category" 
                  dataKey="metric_name" 
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Score']}
                  labelFormatter={(label) => `Metrik: ${label}`}
                />
                <Bar dataKey="normalized_score" name="Performance">
                  {getWeaknessesData().slice(0, 5).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill="#ef4444" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4">
            <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Details</h3>
            <div className="space-y-3">
              {getWeaknessesData().slice(0, 5).map((item, index) => (
                <div key={index} className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-800 dark:text-white">{item.metric_name}</span>
                    <span className="text-red-600 dark:text-red-400 font-semibold">
                      {item.value_formatted}
                    </span>
                  </div>
                  <div className="mt-1 flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Branchendurchschnitt: {item.benchmark_formatted}</span>
                    <span className="text-red-600 dark:text-red-400">
                      {((item.value - item.benchmark) / item.benchmark * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* All Metrics Table */}
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Alle Metriken</h2>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Metrik
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Wert
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Benchmark
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Differenz
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Kategorie
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {analysisData && [...analysisData.strengths, ...analysisData.neutral, ...analysisData.weaknesses].map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {item.metric_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {item.value_formatted}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                    {item.benchmark_formatted}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                    item.category === 'strength' ? 'text-green-500' : 
                    (item.category === 'weakness' ? 'text-red-500' : 'text-gray-500')
                  }`}>
                    {item.difference > 0 ? '+' : ''}{((item.difference) * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      item.category === 'strength' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 
                      (item.category === 'weakness' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' : 
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300')
                    }`}>
                      {item.category_name}
                    </span>
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

export default StrengthWeaknessPage; 