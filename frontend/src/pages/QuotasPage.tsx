import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService, { KPIData, ComparisonData } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import ExportButton from '../components/common/ExportButton';

// Define a type for the scatter data points
interface ScatterDataPoint {
  x: number;
  y: number;
  z: number;
  name: string;
  agency_id: string;
  isSelected: boolean;
  isAverage?: boolean;
}

const QuotasPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        const data = await apiService.compareAgencyKPIs(selectedAgency.agency_id, timePeriod);
        setComparisonData(data);
      } catch (err) {
        console.error('Error fetching KPI comparison data:', err);
        setError('Fehler beim Laden der Vergleichsdaten.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);
  
  if (isLoading) {
    return <Loading message="Laden der KPI-Daten..." />;
  }
  
  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }
  
  if (!selectedAgency || !comparisonData) {
    return (
      <div className="text-center p-8">
        <h2 className="text-xl font-semibold mb-4">Keine Daten verfügbar</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Bitte wählen Sie eine Agentur aus oder versuchen Sie es später erneut.
        </p>
      </div>
    );
  }
  
  // Prepare data for scatter plot
  const scatterData: ScatterDataPoint[] = comparisonData.all_agencies.map(agency => ({
    x: agency.reservation_rate * 100 || 0,  // Convert to percentage
    y: agency.fulfillment_rate * 100 || 0,  // Convert to percentage
    z: agency.total_jobs_reserved || 0,
    name: agency.agency_name,
    agency_id: agency.agency_id,
    isSelected: agency.agency_id === selectedAgency.agency_id,
  }));
  
  // Add industry average
  if (comparisonData.industry_average) {
    scatterData.push({
      x: (comparisonData.industry_average.reservation_rate || 0) * 100,
      y: (comparisonData.industry_average.fulfillment_rate || 0) * 100,
      z: 0,
      name: 'Branchendurchschnitt',
      agency_id: 'industry_average',
      isSelected: false,
      isAverage: true,
    });
  }
  
  const selectedAgencyData = comparisonData.selected_agency;
  
  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;
  
  return (
    <div className="quotas-page">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Quoten: {selectedAgency.agency_name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Kennzahlen und Vergleich mit Branchendurchschnitt
          </p>
        </div>
        <ExportButton 
          targetElementId="quotas-content" 
          filename="quoten-analyse" 
          pageTitle="Quoten-Analyse" 
        />
      </div>
      
      <div id="quotas-content" className="print-container">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="metric-card">
            <h3>Reservierungsrate</h3>
            <div className="value">{formatPercentage(selectedAgencyData.reservation_rate * 100 || 0)}</div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Branchendurchschnitt: {formatPercentage((comparisonData.industry_average.reservation_rate || 0) * 100)}
            </div>
          </div>
          
          <div className="metric-card">
            <h3>Erfüllungsrate</h3>
            <div className="value">{formatPercentage(selectedAgencyData.fulfillment_rate * 100 || 0)}</div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Branchendurchschnitt: {formatPercentage((comparisonData.industry_average.fulfillment_rate || 0) * 100)}
            </div>
          </div>
          
          <div className="metric-card">
            <h3>Abbruchrate</h3>
            <div className="value">{formatPercentage(selectedAgencyData.cancellation_rate * 100 || 0)}</div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Branchendurchschnitt: {formatPercentage((comparisonData.industry_average.cancellation_rate || 0) * 100)}
            </div>
          </div>
        </div>
        
        <div className="dashboard-card mb-8">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Agenturvergleich</h2>
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Jeder Punkt entspricht einer Agentur. Blasengröße repräsentiert die Anzahl der reservierten Stellen.
          </div>
          
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  dataKey="x" 
                  name="Reservierungsrate" 
                  unit="%" 
                  domain={[0, 100]}
                  label={{ value: 'Reservierungsrate (%)', position: 'bottom', offset: 0 }}
                />
                <YAxis 
                  type="number" 
                  dataKey="y" 
                  name="Erfüllungsrate" 
                  unit="%" 
                  domain={[0, 100]}
                  label={{ value: 'Erfüllungsrate (%)', angle: -90, position: 'left' }}
                />
                <ZAxis
                  type="number"
                  dataKey="z"
                  range={[50, 500]}
                  name="Reservierte Stellen"
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: any, name: string) => {
                    if (name === 'Reservierungsrate' || name === 'Erfüllungsrate') {
                      return [`${value}%`, name];
                    }
                    return [value, name];
                  }}
                />
                <Legend />
                <Scatter
                  name="Alle Agenturen"
                  data={scatterData.filter(d => !d.isSelected && !d.isAverage)}
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Scatter
                  name="Ausgewählte Agentur"
                  data={scatterData.filter(d => d.isSelected)}
                  fill="#ff5722"
                  fillOpacity={0.8}
                />
                <Scatter
                  name="Branchendurchschnitt"
                  data={scatterData.filter(d => d.isAverage)}
                  fill="#4caf50"
                  shape="cross"
                  fillOpacity={0.8}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="dashboard-card">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Detaillierte KPIs</h2>
          
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Kennzahl</th>
                  <th>{selectedAgency.agency_name}</th>
                  <th>Branchendurchschnitt</th>
                  <th>Differenz</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Reservierungsrate</td>
                  <td>{formatPercentage(selectedAgencyData.reservation_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.reservation_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.reservation_rate > comparisonData.industry_average.reservation_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.reservation_rate - comparisonData.industry_average.reservation_rate) * 100 || 0)}
                  </td>
                </tr>
                <tr>
                  <td>Erfüllungsrate</td>
                  <td>{formatPercentage(selectedAgencyData.fulfillment_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.fulfillment_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.fulfillment_rate > comparisonData.industry_average.fulfillment_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.fulfillment_rate - comparisonData.industry_average.fulfillment_rate) * 100 || 0)}
                  </td>
                </tr>
                <tr>
                  <td>Abbruchrate</td>
                  <td>{formatPercentage(selectedAgencyData.cancellation_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.cancellation_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.cancellation_rate < comparisonData.industry_average.cancellation_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.cancellation_rate - comparisonData.industry_average.cancellation_rate) * 100 || 0)}
                  </td>
                </tr>
                <tr>
                  <td>Antrittsrate</td>
                  <td>{formatPercentage(selectedAgencyData.start_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.start_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.start_rate > comparisonData.industry_average.start_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.start_rate - comparisonData.industry_average.start_rate) * 100 || 0)}
                  </td>
                </tr>
                <tr>
                  <td>Abschlussrate</td>
                  <td>{formatPercentage(selectedAgencyData.completion_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.completion_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.completion_rate > comparisonData.industry_average.completion_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.completion_rate - comparisonData.industry_average.completion_rate) * 100 || 0)}
                  </td>
                </tr>
                <tr>
                  <td>Vorzeitige Beendigungsrate</td>
                  <td>{formatPercentage(selectedAgencyData.early_end_rate * 100 || 0)}</td>
                  <td>{formatPercentage((comparisonData.industry_average.early_end_rate || 0) * 100)}</td>
                  <td className={selectedAgencyData.early_end_rate < comparisonData.industry_average.early_end_rate ? 'text-green-600' : 'text-red-600'}>
                    {formatPercentage((selectedAgencyData.early_end_rate - comparisonData.industry_average.early_end_rate) * 100 || 0)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuotasPage; 