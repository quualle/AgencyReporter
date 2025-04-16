import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService, { ResponseTimeData, ComparisonData } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import ExportButton from '../components/common/ExportButton';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
} from 'recharts';

interface TopAgency {
  agency_id: string;
  agency_name: string;
  value: number;
}

const ResponseTimesPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [responseTimeData, setResponseTimeData] = useState<ResponseTimeData | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [topAgencies, setTopAgencies] = useState<TopAgency[]>([]);
  const [flopAgencies, setFlopAgencies] = useState<TopAgency[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch data in parallel
        const [responseTimeResponse, comparisonResponse] = await Promise.all([
          apiService.getAgencyResponseTimes(selectedAgency.agency_id, timePeriod),
          apiService.compareAgencyResponseTimes(selectedAgency.agency_id, timePeriod)
        ]);
        
        setResponseTimeData(responseTimeResponse);
        setComparisonData(comparisonResponse);
        
        // Extract top and flop agencies for avg_time_to_reservation
        if (comparisonResponse && comparisonResponse.all_agencies) {
          const sortedAgencies = [...comparisonResponse.all_agencies].sort(
            (a, b) => a.avg_time_to_reservation - b.avg_time_to_reservation
          );
          
          setTopAgencies(sortedAgencies.slice(0, 5).map(agency => ({
            agency_id: agency.agency_id,
            agency_name: agency.agency_name,
            value: agency.avg_time_to_reservation
          })));
          
          setFlopAgencies(sortedAgencies.slice(-5).reverse().map(agency => ({
            agency_id: agency.agency_id,
            agency_name: agency.agency_name,
            value: agency.avg_time_to_reservation
          })));
        }
      } catch (err) {
        console.error('Error fetching response times data:', err);
        setError('Fehler beim Laden der Reaktionszeiten-Daten. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const formatHours = (value: number) => {
    if (value >= 24) {
      return `${(value / 24).toFixed(1)} Tage`;
    }
    return `${value.toFixed(1)} Std.`;
  };

  const getComparisonData = () => {
    if (!comparisonData || !responseTimeData) return [];

    // Transform data for scatter plot
    return comparisonData.all_agencies.map(agency => ({
      agency_id: agency.agency_id,
      agency_name: agency.agency_name,
      x: agency.avg_time_to_reservation || 0,
      y: agency.avg_time_to_proposal || 0,
      z: agency.agency_id === selectedAgency?.agency_id ? 10 : 5,
      isSelected: agency.agency_id === selectedAgency?.agency_id
    }));
  };

  const getTimelineData = () => {
    if (!comparisonData || !responseTimeData) return [];

    // Simulate historical data for line chart (normally would come from API)
    return [
      { month: 'Jan', selected: 45, average: 52 },
      { month: 'Feb', selected: 48, average: 50 },
      { month: 'Mar', selected: 40, average: 48 },
      { month: 'Apr', selected: 38, average: 45 },
      { month: 'Mai', selected: 35, average: 42 },
      { month: 'Jun', selected: responseTimeData.avg_time_to_reservation || 36, average: 40 }
    ];
  };

  if (isLoading) {
    return <Loading message="Reaktionszeiten-Daten werden geladen..." />;
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
    <div className="response-times-page">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Reaktionszeiten: {selectedAgency.agency_name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Analyse der Reaktionszeiten in verschiedenen Phasen des Vermittlungsprozesses
          </p>
        </div>
        <ExportButton 
          targetElementId="response-times-content" 
          filename="reaktionszeiten-analyse" 
          pageTitle="Reaktionszeiten-Analyse" 
        />
      </div>

      <div id="response-times-content" className="print-container">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* KPI Cards */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Reaktionszeiten-Übersicht</h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Ausschreibung → Reservierung:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_reservation ? formatHours(responseTimeData.avg_time_to_reservation) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Reservierung → Personalvorschlag:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_proposal ? formatHours(responseTimeData.avg_time_to_proposal) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Personalvorschlag → Abbruch:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_cancellation ? formatHours(responseTimeData.avg_time_to_cancellation) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Abbruch → geplanter Anreisetermin:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_before_start ? formatHours(responseTimeData.avg_time_before_start) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Zeit bis Abbrüche:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_any_cancellation ? formatHours(responseTimeData.avg_time_to_any_cancellation) : 'N/A'}
                </span>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Vergleich zum Branchendurchschnitt</h3>
              {comparisonData && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Ausschreibung → Reservierung:</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-800 dark:text-white">
                        {formatHours(responseTimeData?.avg_time_to_reservation || 0)}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        vs. {formatHours(comparisonData.industry_average.avg_time_to_reservation || 0)}
                      </span>
                      <span className={`text-xs ${
                        (responseTimeData?.avg_time_to_reservation || 0) < (comparisonData.industry_average.avg_time_to_reservation || 0) 
                          ? 'text-green-500' 
                          : 'text-red-500'
                      }`}>
                        {(responseTimeData?.avg_time_to_reservation || 0) < (comparisonData.industry_average.avg_time_to_reservation || 0) 
                          ? '✓' 
                          : '✗'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Reservierung → Personalvorschlag:</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-800 dark:text-white">
                        {formatHours(responseTimeData?.avg_time_to_proposal || 0)}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        vs. {formatHours(comparisonData.industry_average.avg_time_to_proposal || 0)}
                      </span>
                      <span className={`text-xs ${
                        (responseTimeData?.avg_time_to_proposal || 0) < (comparisonData.industry_average.avg_time_to_proposal || 0) 
                          ? 'text-green-500' 
                          : 'text-red-500'
                      }`}>
                        {(responseTimeData?.avg_time_to_proposal || 0) < (comparisonData.industry_average.avg_time_to_proposal || 0) 
                          ? '✓' 
                          : '✗'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Time Trend Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Zeitverlauf: Reaktionszeiten</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={getTimelineData()} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
                  <XAxis dataKey="month" />
                  <YAxis label={{ value: 'Stunden', angle: -90, position: 'insideLeft' }} />
                  <Tooltip
                    formatter={(value: number) => [formatHours(value), 'Reaktionszeit']}
                    labelFormatter={(label) => `Monat: ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="selected" 
                    name={selectedAgency.agency_name} 
                    stroke="#4f46e5" 
                    strokeWidth={2} 
                    dot={{ r: 4 }} 
                    activeDot={{ r: 6 }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="average" 
                    name="Branchendurchschnitt" 
                    stroke="#9ca3af" 
                    strokeWidth={2} 
                    dot={{ r: 4 }} 
                    strokeDasharray="4 4" 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Scatter Plot for Comparison */}
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Agenturvergleich: Reaktionszeiten</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Vergleich der Reaktionszeiten aller Agenturen. Die X-Achse zeigt die Zeit von Ausschreibung bis Reservierung, 
            die Y-Achse die Zeit von Reservierung bis Personalvorschlag.
          </p>
          
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
                <XAxis 
                  type="number" 
                  dataKey="x" 
                  name="Zeit bis Reservierung" 
                  label={{ value: 'Stunden bis Reservierung', position: 'bottom', offset: 0 }}
                  tickFormatter={formatHours}
                />
                <YAxis 
                  type="number" 
                  dataKey="y" 
                  name="Zeit bis Personalvorschlag" 
                  label={{ value: 'Stunden bis Personalvorschlag', angle: -90, position: 'left' }}
                  tickFormatter={formatHours}
                />
                <ZAxis type="number" dataKey="z" range={[40, 100]} name="Größe" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: number, name: string) => [formatHours(value), name]}
                  labelFormatter={(label) => ''}
                  content={(props) => {
                    if (props.active && props.payload && props.payload.length) {
                      const data = props.payload[0].payload;
                      return (
                        <div className="bg-white dark:bg-gray-800 p-2 border border-gray-200 dark:border-gray-700 shadow-sm rounded">
                          <p className="font-medium">{data.agency_name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Zeit bis Reservierung: {formatHours(data.x)}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Zeit bis Personalvorschlag: {formatHours(data.y)}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Agenturen" data={getComparisonData()}>
                  {getComparisonData().map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.isSelected ? '#4f46e5' : '#9ca3af'} 
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top/Flop Lists */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Top 5 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Top 5 - Schnellste Reaktionszeiten</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={topAgencies}
                  margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#ccc" horizontal={false} />
                  <XAxis type="number" tickFormatter={formatHours} />
                  <YAxis 
                    type="category" 
                    dataKey="agency_name" 
                    tick={{ fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip 
                    formatter={(value: number) => [formatHours(value), 'Reaktionszeit']}
                    labelFormatter={(label) => `Agentur: ${label}`}
                  />
                  <Bar 
                    dataKey="value" 
                    fill="#10b981" 
                    name="Reaktionszeit"
                  >
                    {topAgencies.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.agency_id === selectedAgency?.agency_id ? '#4f46e5' : '#10b981'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Flop 5 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Flop 5 - Langsamste Reaktionszeiten</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={flopAgencies}
                  margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#ccc" horizontal={false} />
                  <XAxis type="number" tickFormatter={formatHours} />
                  <YAxis 
                    type="category" 
                    dataKey="agency_name" 
                    tick={{ fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip 
                    formatter={(value: number) => [formatHours(value), 'Reaktionszeit']}
                    labelFormatter={(label) => `Agentur: ${label}`}
                  />
                  <Bar 
                    dataKey="value" 
                    fill="#ef4444" 
                    name="Reaktionszeit"
                  >
                    {flopAgencies.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.agency_id === selectedAgency?.agency_id ? '#4f46e5' : '#ef4444'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseTimesPage; 