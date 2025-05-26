import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { apiService, preloadService } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import CacheStats from '../components/common/CacheStats';

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
  total_confirmed: number;
  total_started: number;
}

interface AgencyCompletionData {
  agency_id: string;
  agency_name: string;
  completion_rate: number;
  early_termination_rate: number;
  total_started: number;
  total_completed: number;
}

const Dashboard: React.FC = () => {
  const { timePeriod, setPreloadStatus, setShowPreloadOverlay } = useAppStore();
  const [problematicData, setProblematicData] = useState<AgencyProblematicData[]>([]);
  const [conversionData, setConversionData] = useState<AgencyConversionData[]>([]);
  const [completionData, setCompletionData] = useState<AgencyCompletionData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAllProblematic, setShowAllProblematic] = useState<boolean>(false);
  const [showAllConversion, setShowAllConversion] = useState<boolean>(false);
  const [showAllCompletion, setShowAllCompletion] = useState<boolean>(false);
  const [isPreloading, setIsPreloading] = useState<boolean>(false);

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

        // Schritt 2: Echte Conversion-Daten für alle Agenturen laden
        const conversionResponse = await apiService.getAllAgenciesConversionStats(timePeriod, false, true);
        console.log('Dashboard conversion data:', conversionResponse);
        
        // API wraps data in {data: [...]} format
        const conversionArray = conversionResponse?.data || conversionResponse;
        
        if (conversionArray && Array.isArray(conversionArray)) {
          // Echte Daten verarbeiten und sortieren
          const sortedConversionData = conversionArray
            .map((item: any) => ({
              agency_id: item.agency_id,
              agency_name: item.agency_name,
              start_rate: item.start_rate || 0,
              cancellation_rate: item.cancellation_rate || 0,
              total_postings: item.total_postings || 0,
              total_confirmed: item.total_confirmed || 0,
              total_started: item.total_started || 0
            }))
            .sort((a: AgencyConversionData, b: AgencyConversionData) => 
              a.start_rate - b.start_rate // Niedrigere start_rate = höhere Abbruchrate, also umgekehrt sortieren
            );
          
          setConversionData(sortedConversionData);
        } else {
          console.warn('Unexpected conversion data format:', conversionResponse);
          setConversionData([]);
        }

        // Schritt 3: Completion-Daten für alle Agenturen laden
        const completionResponse = await apiService.getAllAgenciesCompletionStats(timePeriod, false, true);
        console.log('Dashboard completion data:', completionResponse);
        
        // API wraps data in {data: [...]} format
        const completionArray = completionResponse?.data || completionResponse;
        
        if (completionArray && Array.isArray(completionArray)) {
          // Echte Daten verarbeiten und sortieren
          const sortedCompletionData = completionArray
            .map((item: any) => ({
              agency_id: item.agency_id,
              agency_name: item.agency_name,
              completion_rate: item.completion_rate || 0,
              early_termination_rate: item.early_termination_rate || 0,
              total_started: item.total_started || 0,
              total_completed: item.total_completed || 0
            }))
            .sort((a: AgencyCompletionData, b: AgencyCompletionData) => 
              b.early_termination_rate - a.early_termination_rate // Höchste Abbruchrate zuerst
            );
          
          setCompletionData(sortedCompletionData);
        } else {
          console.warn('Unexpected completion data format:', completionResponse);
          setCompletionData([]);
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

  const getConversionColor = (cancellationRate: number): string => {
    if (cancellationRate <= 15) return 'bg-green-500';
    if (cancellationRate <= 30) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConversionTextColor = (cancellationRate: number): string => {
    if (cancellationRate <= 15) return 'text-green-700 dark:text-green-300';
    if (cancellationRate <= 30) return 'text-yellow-700 dark:text-yellow-300';
    return 'text-red-700 dark:text-red-300';
  };

  const getCompletionColor = (earlyTerminationRate: number): string => {
    if (earlyTerminationRate <= 20) return 'bg-green-500';
    if (earlyTerminationRate <= 35) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getCompletionTextColor = (earlyTerminationRate: number): string => {
    if (earlyTerminationRate <= 20) return 'text-green-700 dark:text-green-300';
    if (earlyTerminationRate <= 35) return 'text-yellow-700 dark:text-yellow-300';
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
  const displayCompletionData = showAllCompletion ? completionData : completionData.slice(0, 5);

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

      {/* Cache Status und Preload Button */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <CacheStats showDetails={false} />
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Dashboard-Daten vorladen</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
              Lädt alle Dashboard-Daten für optimale Performance
            </p>
          </div>
          <button
            onClick={async () => {
              setIsPreloading(true);
              setShowPreloadOverlay(true);
              setPreloadStatus({
                totalRequests: 0,
                completedRequests: 0,
                inProgress: true,
                status: 'Starte Dashboard-Datenladung...'
              });
              
              try {
                await preloadService.preloadDashboardData(
                  timePeriod,
                  (progress) => {
                    setPreloadStatus(progress);
                  }
                );
              } catch (error) {
                console.error('Dashboard preload failed:', error);
                setPreloadStatus({
                  totalRequests: 0,
                  completedRequests: 0,
                  inProgress: false,
                  status: 'Fehler beim Laden der Dashboard-Daten',
                  error: error instanceof Error ? error.message : 'Unbekannter Fehler'
                });
              } finally {
                setIsPreloading(false);
                // Reload dashboard data after preloading
                window.location.reload();
              }
            }}
            disabled={isPreloading}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              isPreloading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isPreloading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Lädt...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2 inline" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Daten vorladen
              </>
            )}
          </button>
        </div>
      </div>

      {/* Top Section: 3 Widgets nebeneinander */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
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
                🚌 Probleme vor der Anreise
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Priorität: 8)
                </span>
              </h2>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Abbrüche zwischen Bestätigung und Anreise
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
                    <div className={`w-2 h-2 rounded-full ${getConversionColor(100 - agency.start_rate)}`}></div>
                    <div>
                      <h3 className="font-medium text-gray-800 dark:text-white text-sm">
                        {agency.agency_name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-300">
                        {agency.total_confirmed} Bestätigte, {agency.total_confirmed - agency.total_started} Abgebrochen
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getConversionTextColor(100 - agency.start_rate)}`}>
                      {(100 - agency.start_rate).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      Abbruch vor Anreise
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
        </div>

        {/* Widget 3: Durchführungsrate */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white flex items-center">
                🏠 Probleme nach der Anreise
                <span className="ml-2 text-sm font-normal text-gray-500">
                  (Priorität: 7)
                </span>
              </h2>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Vorzeitige Beendigungen nach Anreise
              </p>
            </div>
            <button
              onClick={() => setShowAllCompletion(!showAllCompletion)}
              className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
            >
              {showAllCompletion ? 'Top 5' : 'Alle'} 
              <span className="ml-1">{showAllCompletion ? '▲' : '▼'}</span>
            </button>
          </div>

          {completionData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Keine Durchführungs-Daten verfügbar
            </div>
          ) : (
            <div className="space-y-2">
              {displayCompletionData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-400 w-6">
                      #{index + 1}
                    </span>
                    <div className={`w-2 h-2 rounded-full ${getCompletionColor(agency.early_termination_rate)}`}></div>
                    <div>
                      <h3 className="font-medium text-gray-800 dark:text-white text-sm">
                        {agency.agency_name}
                      </h3>
                      <p className="text-xs text-gray-600 dark:text-gray-300">
                        {agency.total_started} Angetreten, {agency.total_started - agency.total_completed} Vorzeitig beendet
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getCompletionTextColor(agency.early_termination_rate)}`}>
                      {agency.early_termination_rate.toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      Vorzeitig beendet
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {showAllCompletion && completionData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {completionData.length} Agenturen
            </div>
          )}
        </div>
      </div>

      {/* Placeholder für weitere Widgets */}
      <div className="text-center py-12 text-gray-500">
        <div className="text-4xl mb-4">🚧</div>
        <h3 className="text-lg font-medium mb-2">Weitere Widgets folgen</h3>
        <p>5 weitere Dashboard-Widgets werden schrittweise implementiert</p>
      </div>
    </div>
  );
};

export default Dashboard; 