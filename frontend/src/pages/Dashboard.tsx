import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { apiService } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

interface AgencyProblematicData {
  agency_id: string;
  agency_name: string;
  total_problematic: number;
  total_stays: number;
  problematic_rate: number;
}

interface AgencyConversionData {
  agency_id: string;
  agency_name: string;
  start_rate: number;
  cancellation_rate: number;
  total_postings: number;
}

const Dashboard: React.FC = () => {
  const { timePeriod } = useAppStore();
  const [problematicData, setProblematicData] = useState<AgencyProblematicData[]>([]);
  const [conversionData, setConversionData] = useState<AgencyConversionData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAllProblematic, setShowAllProblematic] = useState<boolean>(false);
  const [showAllConversion, setShowAllConversion] = useState<boolean>(false);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Schritt 1: Problematische Einsätze laden
        const problematicResponse = await apiService.getProblematicStaysOverview(undefined, timePeriod, false, true);
        
        console.log('Dashboard problematic stays data:', problematicResponse);
        
        if (problematicResponse && problematicResponse.data && Array.isArray(problematicResponse.data)) {
          // Daten nach problematic_percentage sortieren (höchste zuerst)
          const sortedProblematicData = problematicResponse.data
            .map((item: any) => ({
              agency_id: item.agency_id,
              agency_name: item.agency_name,
              total_problematic: item.total_problematic || 0,
              total_stays: item.total_carestays || 0, // Korrektes Feld aus SQL
              problematic_rate: item.problematic_percentage || 0 // Korrektes Feld aus SQL
            }))
            .sort((a: AgencyProblematicData, b: AgencyProblematicData) => 
              b.problematic_rate - a.problematic_rate
            );
          
          setProblematicData(sortedProblematicData);
        } else {
          console.warn('Unexpected problematic data format:', problematicResponse);
          setProblematicData([]);
        }

        // Schritt 2: Alle Agenturen für Conversion-Daten laden
        const agenciesResponse = await apiService.getAgencies();
        console.log('Dashboard agencies data:', agenciesResponse);
        
        if (agenciesResponse && Array.isArray(agenciesResponse)) {
          // Für Demo: Simuliere Conversion-Daten basierend auf Agenturen
          // TODO: Implementiere echte API für alle Agenturen Quotas
          const conversionDataTemp = agenciesResponse
            .map((agency: any) => ({
              agency_id: agency.agency_id,
              agency_name: agency.agency_name,
              start_rate: Math.random() * 30 + 70, // Demo: 70-100%
              cancellation_rate: Math.random() * 30, // Demo: 0-30%
              total_postings: Math.floor(Math.random() * 500) + 50 // Demo: 50-550
            }))
            .sort((a: AgencyConversionData, b: AgencyConversionData) => 
              b.start_rate - a.start_rate
            );
          
          setConversionData(conversionDataTemp);
        } else {
          console.warn('Unexpected agencies data format:', agenciesResponse);
          setConversionData([]);
        }
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Fehler beim Laden der Dashboard-Daten.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [timePeriod]);

  const getStatusColor = (rate: number): string => {
    if (rate >= 15) return 'bg-red-500';
    if (rate >= 10) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusTextColor = (rate: number): string => {
    if (rate >= 15) return 'text-red-700 dark:text-red-300';
    if (rate >= 10) return 'text-yellow-700 dark:text-yellow-300';
    return 'text-green-700 dark:text-green-300';
  };

  const getConversionColor = (rate: number): string => {
    if (rate >= 90) return 'bg-green-500';
    if (rate >= 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConversionTextColor = (rate: number): string => {
    if (rate >= 90) return 'text-green-700 dark:text-green-300';
    if (rate >= 80) return 'text-yellow-700 dark:text-yellow-300';
    return 'text-red-700 dark:text-red-300';
  };

  if (isLoading) {
    return <Loading message="Dashboard-Daten werden geladen..." />;
  }

  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }

  const displayProblematicData = showAllProblematic ? problematicData : problematicData.slice(0, 5);
  const displayConversionData = showAllConversion ? conversionData : conversionData.slice(0, 5);

  return (
    <div className="dashboard">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
          Dashboard - Agenturvergleich
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Vergleichende Übersicht aller Agenturen
        </p>
      </div>

      {/* Top Section: 2 Widgets nebeneinander */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Widget 1: Problematische Einsätze */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white flex items-center">
                🚨 Problematische Einsätze
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Priorität: 9)
                </span>
              </h2>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Agenturen mit den höchsten Problemraten
              </p>
            </div>
            <button
              onClick={() => setShowAllProblematic(!showAllProblematic)}
              className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
            >
              {showAllProblematic ? 'Top 5' : 'Alle'} 
              <span className="ml-1">{showAllProblematic ? '▲' : '▼'}</span>
            </button>
          </div>

          {problematicData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Keine Daten verfügbar
            </div>
          ) : (
            <div className="space-y-2">
              {displayProblematicData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-400 w-6">
                      #{index + 1}
                    </span>
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(agency.problematic_rate)}`}></div>
                    <div>
                      <h3 className="font-medium text-gray-800 dark:text-white text-sm">
                        {agency.agency_name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-300">
                        {agency.total_problematic} von {agency.total_stays}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getStatusTextColor(agency.problematic_rate)}`}>
                      {agency.problematic_rate.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {showAllProblematic && problematicData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {problematicData.length} Agenturen
            </div>
          )}
        </div>

        {/* Widget 2: Conversion Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white flex items-center">
                ⚖️ Conversion Performance
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Priorität: 8)
                </span>
              </h2>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Ausschreibung → Start (beste Startraten)
              </p>
            </div>
            <button
              onClick={() => setShowAllConversion(!showAllConversion)}
              className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
            >
              {showAllConversion ? 'Top 5' : 'Alle'} 
              <span className="ml-1">{showAllConversion ? '▲' : '▼'}</span>
            </button>
          </div>

          {conversionData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Keine Conversion-Daten verfügbar
            </div>
          ) : (
            <div className="space-y-2">
              {displayConversionData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-400 w-6">
                      #{index + 1}
                    </span>
                    <div className={`w-2 h-2 rounded-full ${getConversionColor(agency.start_rate)}`}></div>
                    <div>
                      <h3 className="font-medium text-gray-800 dark:text-white text-sm">
                        {agency.agency_name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-300">
                        {agency.total_postings} Ausschreibungen
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getConversionTextColor(agency.start_rate)}`}>
                      {agency.start_rate.toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      Startrate
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {showAllConversion && conversionData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {conversionData.length} Agenturen
            </div>
          )}
          
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700">
            <p className="text-xs text-yellow-800 dark:text-yellow-200">
              ⚠️ Demo-Daten: Echte Quotas-API für alle Agenturen wird noch implementiert
            </p>
          </div>
        </div>
      </div>

      {/* Placeholder für weitere Widgets */}
      <div className="text-center py-12 text-gray-500">
        <div className="text-4xl mb-4">🚧</div>
        <h3 className="text-lg font-medium mb-2">Weitere Widgets folgen</h3>
        <p>7 weitere Dashboard-Widgets werden schrittweise implementiert</p>
      </div>
    </div>
  );
};

export default Dashboard; 