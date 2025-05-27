import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { apiService } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import StayDetailsModal from '../components/common/StayDetailsModal';
import InfoModal from '../components/common/InfoModal';

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
  const { timePeriod } = useAppStore();
  const [problematicData, setProblematicData] = useState<AgencyProblematicData[]>([]);
  const [conversionData, setConversionData] = useState<AgencyConversionData[]>([]);
  const [completionData, setCompletionData] = useState<AgencyCompletionData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAllProblematic, setShowAllProblematic] = useState<boolean>(false);
  const [showAllConversion, setShowAllConversion] = useState<boolean>(false);
  const [showAllCompletion, setShowAllCompletion] = useState<boolean>(false);
  const [minStaysFilter, setMinStaysFilter] = useState<number>(0);
  
  // Modal state
  const [modalData, setModalData] = useState<{
    isOpen: boolean;
    agencyId: string;
    agencyName: string;
    title: string;
    detailType: 'problematic' | 'cancellations' | 'terminations';
  }>({
    isOpen: false,
    agencyId: '',
    agencyName: '',
    title: '',
    detailType: 'problematic'
  });
  
  // State für Info-Modals
  const [infoModalOpen, setInfoModalOpen] = useState<'problematic' | 'cancellations' | 'terminations' | null>(null);

  useEffect(() => {
    console.log('🔄 Dashboard useEffect triggered with timePeriod:', timePeriod);
    
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        console.log(`📊 Fetching dashboard data for period: ${timePeriod}`);
        
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
        console.log(`📊 Fetching conversion stats for period: ${timePeriod}`);
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
        console.log(`📊 Fetching completion stats for period: ${timePeriod}`);
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
    if (earlyTerminationRate <= 25) return 'bg-green-500';
    if (earlyTerminationRate <= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getCompletionTextColor = (earlyTerminationRate: number): string => {
    if (earlyTerminationRate <= 25) return 'text-green-700 dark:text-green-300';
    if (earlyTerminationRate <= 40) return 'text-yellow-700 dark:text-yellow-300';
    return 'text-red-700 dark:text-red-300';
  };

  if (isLoading) {
    return <Loading message="Dashboard-Daten werden geladen..." />;
  }

  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }

  // Filter data based on minimum stays
  const filteredProblematicData = problematicData.filter(agency => agency.total_stays >= minStaysFilter);
  const filteredConversionData = conversionData.filter(agency => agency.total_confirmed >= minStaysFilter);
  const filteredCompletionData = completionData.filter(agency => agency.total_started >= minStaysFilter);

  // Display data based on show all toggle
  const displayProblematicData = showAllProblematic ? filteredProblematicData : filteredProblematicData.slice(0, 5);
  const displayConversionData = showAllConversion ? filteredConversionData : filteredConversionData.slice(0, 5);
  const displayCompletionData = showAllCompletion ? filteredCompletionData : filteredCompletionData.slice(0, 5);

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


      {/* Filter Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center justify-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Nur Agenturen mit mindestens
          </label>
          <input
            type="number"
            min="0"
            max="300"
            value={minStaysFilter}
            onChange={(e) => setMinStaysFilter(Math.max(0, Math.min(300, parseInt(e.target.value) || 0)))}
            className="w-20 px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">
            Einsätzen
          </span>
          {minStaysFilter > 0 && (
            <button
              onClick={() => setMinStaysFilter(0)}
              className="ml-4 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              Filter zurücksetzen
            </button>
          )}
        </div>
      </div>

      {/* Top Section: 3 Widgets nebeneinander */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Widget 1: Problematische Einsätze */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex-1">
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
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setInfoModalOpen('problematic')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Information anzeigen"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                onClick={() => setShowAllProblematic(!showAllProblematic)}
                className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
              >
                {showAllProblematic ? 'Top 5' : 'Alle'} 
                <span className="ml-1">{showAllProblematic ? '▲' : '▼'}</span>
              </button>
            </div>
          </div>

          {filteredProblematicData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {minStaysFilter > 0 
                ? `Keine Agenturen mit mindestens ${minStaysFilter} Einsätzen gefunden`
                : 'Keine Daten verfügbar'}
            </div>
          ) : (
            <div className="space-y-2">
              {displayProblematicData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                  onClick={() => setModalData({
                    isOpen: true,
                    agencyId: agency.agency_id,
                    agencyName: agency.agency_name,
                    title: 'Problematische Einsätze',
                    detailType: 'problematic'
                  })}
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

          {showAllProblematic && filteredProblematicData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {filteredProblematicData.length} Agenturen
            </div>
          )}
        </div>

        {/* Widget 2: Conversion Performance */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex-1">
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
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setInfoModalOpen('cancellations')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Information anzeigen"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                onClick={() => setShowAllConversion(!showAllConversion)}
                className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
              >
                {showAllConversion ? 'Top 5' : 'Alle'} 
                <span className="ml-1">{showAllConversion ? '▲' : '▼'}</span>
              </button>
            </div>
          </div>

          {filteredConversionData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {minStaysFilter > 0 
                ? `Keine Agenturen mit mindestens ${minStaysFilter} bestätigten Einsätzen gefunden`
                : 'Keine Conversion-Daten verfügbar'}
            </div>
          ) : (
            <div className="space-y-2">
              {displayConversionData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                  onClick={() => setModalData({
                    isOpen: true,
                    agencyId: agency.agency_id,
                    agencyName: agency.agency_name,
                    title: 'Probleme vor der Anreise',
                    detailType: 'cancellations'
                  })}
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

          {showAllConversion && filteredConversionData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {filteredConversionData.length} Agenturen
            </div>
          )}
        </div>

        {/* Widget 3: Durchführungsrate */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex-1">
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
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setInfoModalOpen('terminations')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Information anzeigen"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                onClick={() => setShowAllCompletion(!showAllCompletion)}
                className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs transition-colors"
              >
                {showAllCompletion ? 'Top 5' : 'Alle'} 
                <span className="ml-1">{showAllCompletion ? '▲' : '▼'}</span>
              </button>
            </div>
          </div>

          {filteredCompletionData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {minStaysFilter > 0 
                ? `Keine Agenturen mit mindestens ${minStaysFilter} angetretenen Einsätzen gefunden`
                : 'Keine Durchführungs-Daten verfügbar'}
            </div>
          ) : (
            <div className="space-y-2">
              {displayCompletionData.map((agency, index) => (
                <div 
                  key={agency.agency_id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                  onClick={() => setModalData({
                    isOpen: true,
                    agencyId: agency.agency_id,
                    agencyName: agency.agency_name,
                    title: 'Probleme nach der Anreise',
                    detailType: 'terminations'
                  })}
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
                        {agency.total_started} Abgeschlossen, {agency.total_started - agency.total_completed} Vorzeitig beendet
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

          {showAllCompletion && filteredCompletionData.length > 5 && (
            <div className="mt-3 text-center text-xs text-gray-500">
              Zeige alle {filteredCompletionData.length} Agenturen
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
      
      {/* Details Modal */}
      <StayDetailsModal
        isOpen={modalData.isOpen}
        onClose={() => setModalData({ ...modalData, isOpen: false })}
        agencyId={modalData.agencyId}
        agencyName={modalData.agencyName}
        title={modalData.title}
        detailType={modalData.detailType}
        timePeriod={timePeriod}
      />
      
      {/* Info Modals */}
      {infoModalOpen && (
        <InfoModal
          isOpen={true}
          onClose={() => setInfoModalOpen(null)}
          type={infoModalOpen}
        />
      )}
    </div>
  );
};

export default Dashboard; 