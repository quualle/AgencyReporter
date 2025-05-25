import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { apiService } from '../services/api';
import InstantDepartureWidget from '../components/problematic_stays/InstantDepartureWidget';
import CustomerSatisfactionWidget from '../components/problematic_stays/CustomerSatisfactionWidget';
import TrendAnalysisWidget from '../components/problematic_stays/TrendAnalysisWidget';
import OverviewWidget from '../components/problematic_stays/OverviewWidget';
import DistributionWidget from '../components/problematic_stays/DistributionWidget';
import CancellationLeadTimeWidget from '../components/problematic_stays/CancellationLeadTimeWidget';
import ReasonListWidget from '../components/problematic_stays/ReasonListWidget';
import TimeAnalysisWidget from '../components/problematic_stays/TimeAnalysisWidget';
import AgencySelector from '../components/common/AgencySelector';

console.log('🔥 ProblematicStaysPage LOADED - NEW VERSION WITH APISERVICE');
console.log('🔥 apiService imported:', apiService);
console.log('🔥 getProblematicStaysOverview method:', apiService.getProblematicStaysOverview);

const ProblematicStaysPage: React.FC = () => {
  const { timePeriod, selectedAgency, setActiveTab } = useAppStore();
  
  // State für die verschiedenen Daten
  const [overviewData, setOverviewData] = useState<any>({ data: [] });
  const [reasonsData, setReasonsData] = useState<any>({ data: [] });
  const [timeAnalysisData, setTimeAnalysisData] = useState<any>({ data: [] });
  const [heatmapData, setHeatmapData] = useState<any>({ data: [] });
  const [instantDeparturesData, setInstantDeparturesData] = useState<any>({ data: [] });
  const [replacementData, setReplacementData] = useState<any>({ data: [] });
  const [satisfactionData, setSatisfactionData] = useState<any>({ data: [] });
  const [trendData, setTrendData] = useState<any>({ data: [] });
  const [cancellationLeadTimeData, setCancellationLeadTimeData] = useState<any>({ data: [] });
  
  // Loading States
  const [isOverviewLoading, setIsOverviewLoading] = useState<boolean>(true);
  const [isReasonsLoading, setIsReasonsLoading] = useState<boolean>(true);
  const [isTimeAnalysisLoading, setIsTimeAnalysisLoading] = useState<boolean>(true);
  const [isHeatmapLoading, setIsHeatmapLoading] = useState<boolean>(true);
  const [isInstantDeparturesLoading, setIsInstantDeparturesLoading] = useState<boolean>(true);
  const [isReplacementLoading, setIsReplacementLoading] = useState<boolean>(true);
  const [isSatisfactionLoading, setIsSatisfactionLoading] = useState<boolean>(true);
  const [isTrendLoading, setIsTrendLoading] = useState<boolean>(true);
  const [isCancellationLeadTimeLoading, setIsCancellationLeadTimeLoading] = useState<boolean>(true);
  
  // Gemeinsamer Ladezustand für die gesamte Seite
  const [isPageLoading, setIsPageLoading] = useState<boolean>(true);
  // Fortschritt der Ladung in Prozent
  const [loadingProgress, setLoadingProgress] = useState<number>(0);

  // Tab-Zustand für aktiven Tab
  React.useEffect(() => {
    setActiveTab('problematic-stays');
  }, [setActiveTab]);

  // Daten laden
  useEffect(() => {
    const fetchData = async () => {
      // Debug logging for state changes
      console.log('🔄 ProblematicStaysPage useEffect triggered:', { 
        selectedAgency: selectedAgency?.agency_name, 
        agencyId: selectedAgency?.agency_id,
        timePeriod,
        currentOverviewDataLength: overviewData?.data?.length 
      });
      
      const agencyId = selectedAgency ? selectedAgency.agency_id : undefined;
      
      // Prüfen ob bereits Daten für diese Kombination vorhanden sind
      const hasValidData = overviewData?.data && overviewData.data.length > 0;
      const currentAgencyInData = overviewData?.data?.[0]?.agency_id;
      const dataMatchesCurrentSelection = !agencyId || currentAgencyInData === agencyId;
      
      if (hasValidData && dataMatchesCurrentSelection) {
        console.log('🚀 Skipping data reload - valid cached data exists');
        return;
      }
      
      // Seite als "wird geladen" markieren
      setIsPageLoading(true);
      setLoadingProgress(0);
      
      try {
        // Alle Anfragen parallel starten anstatt sequentiell
        const requests = [
          // Übersichtsdaten
          {
            request: apiService.getProblematicStaysOverview(agencyId, timePeriod),
            setData: setOverviewData,
            setLoading: setIsOverviewLoading
          },
          // Gründe
          {
            request: apiService.getProblematicStaysReasons(agencyId, undefined, timePeriod),
            setData: setReasonsData,
            setLoading: setIsReasonsLoading
          },
          // Zeitliche Analyse
          {
            request: apiService.getProblematicStaysTimeAnalysis(agencyId, undefined, undefined, timePeriod),
            setData: setTimeAnalysisData,
            setLoading: setIsTimeAnalysisLoading
          },
          // Heatmap-Daten
          {
            request: apiService.getProblematicStaysHeatmap(agencyId, undefined, undefined, timePeriod),
            setData: setHeatmapData,
            setLoading: setIsHeatmapLoading
          },
          // Instant Departures
          {
            request: apiService.getProblematicStaysInstantDepartures(agencyId, timePeriod),
            setData: setInstantDeparturesData,
            setLoading: setIsInstantDeparturesLoading
          },
          // Ersatz-Analyse
          {
            request: apiService.getProblematicStaysReplacementAnalysis(agencyId, timePeriod),
            setData: setReplacementData,
            setLoading: setIsReplacementLoading
          },
          // Kundenzufriedenheit
          {
            request: apiService.getProblematicStaysCustomerSatisfaction(agencyId, timePeriod),
            setData: setSatisfactionData,
            setLoading: setIsSatisfactionLoading
          },
          // Trend-Analyse (immer letztes Jahr)
          {
            request: apiService.getProblematicStaysTrendAnalysis(agencyId, undefined, undefined, 'last_year'),
            setData: setTrendData,
            setLoading: setIsTrendLoading
          },
          // Abbrüche - Vorlaufzeit
          {
            request: apiService.getProblematicStaysCancellationLeadTime(agencyId, timePeriod),
            setData: setCancellationLeadTimeData,
            setLoading: setIsCancellationLeadTimeLoading
          }
        ];
        
        // Alle Ladestates auf "laden" setzen
        requests.forEach(item => item.setLoading(true));
        
        // Fortschritt verfolgen
        let completedRequests = 0;
        const totalRequests = requests.length;
        
        // Parallel ausführen
        await Promise.all(
          requests.map(async (item, index) => {
            try {
              const data = await item.request;
              // API responses have a 'data' field containing the array, or the response itself is the data
              const safeData = data && typeof data === 'object' ? data : {};
              item.setData(safeData);
              item.setLoading(false);
              
              // Fortschritt aktualisieren
              completedRequests++;
              setLoadingProgress(Math.round((completedRequests / totalRequests) * 100));
            } catch (error) {
              console.error(`Fehler beim Laden (${index}):`, error);
              // Set empty object as fallback data
              item.setData({ data: [] });
              item.setLoading(false);
              
              // Update progress even on error
              completedRequests++;
              setLoadingProgress(Math.round((completedRequests / totalRequests) * 100));
            }
          })
        );
        
        // Seite als "geladen" markieren
        setIsPageLoading(false);
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error);
        // Bei Fehler auch Ladevorgang beenden
        setIsOverviewLoading(false);
        setIsReasonsLoading(false);
        setIsTimeAnalysisLoading(false);
        setIsHeatmapLoading(false);
        setIsInstantDeparturesLoading(false);
        setIsReplacementLoading(false);
        setIsSatisfactionLoading(false);
        setIsTrendLoading(false);
        setIsCancellationLeadTimeLoading(false);
        setIsPageLoading(false);
      }
    };

    fetchData();
  }, [selectedAgency?.agency_id, timePeriod]);

  // Gesamtzahl der Einsätze extrahieren
  const totalCareStays = overviewData?.data && overviewData.data.length > 0 ? overviewData.data[0].total_carestays : 0;
  const totalProblematic = overviewData?.data && overviewData.data.length > 0 ? overviewData.data[0].total_problematic : 0;
  const problematicPercentage = overviewData?.data && overviewData.data.length > 0 ? overviewData.data[0].problematic_percentage : 0;

  // Lade-Overlay anzeigen, während die Daten geladen werden
  if (isPageLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="fixed inset-0 flex items-center justify-center bg-white dark:bg-gray-900 bg-opacity-80 dark:bg-opacity-80 z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
              Daten werden geladen... {loadingProgress}%
            </h2>
            <div className="w-64 bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-4">
              <div className="bg-primary-600 h-2.5 rounded-full" style={{ width: `${loadingProgress}%` }}></div>
            </div>
            <p className="text-gray-600 dark:text-gray-300 max-w-md">
              Bitte haben Sie einen Moment Geduld, während wir die Analysedaten für problematische Pflegeeinsätze vorbereiten.
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Problematische Pflegeeinsätze - Analyse
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Übersicht und Analysen zu abgebrochenen und vorzeitig beendeten Pflegeeinsätzen.
          </p>
        </div>

        <div className="mb-6">
          <AgencySelector />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Problematische Pflegeeinsätze - Analyse
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Übersicht und Analysen zu abgebrochenen und vorzeitig beendeten Pflegeeinsätzen.
        </p>
      </div>

      {/* Gesamtstatistik */}
      {!isOverviewLoading && overviewData?.data && overviewData.data.length > 0 && (
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex flex-wrap items-center justify-between">
            <div className="flex items-center">
              <div className="text-3xl font-bold text-gray-900 dark:text-white">{totalCareStays.toLocaleString()}</div>
              <div className="ml-2 text-gray-600 dark:text-gray-300">Einsätze gesamt</div>
            </div>
            <div className="flex items-center mt-2 md:mt-0">
              <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">{totalProblematic.toLocaleString()}</div>
              <div className="ml-2 text-gray-600 dark:text-gray-300">
                problematische Einsätze ({problematicPercentage.toFixed(1)}%)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Übersichts-Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <OverviewWidget 
            data={overviewData?.data || []} 
            isLoading={isOverviewLoading} 
          />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <DistributionWidget 
            data={overviewData?.data || []} 
            isLoading={isOverviewLoading} 
          />
        </div>
      </div>

      {/* Zeitliche Entwicklung */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Problematische Einsätze - Zeitliche Entwicklung</h2>
          <TrendAnalysisWidget 
            data={trendData?.data || []} 
            isLoading={isTrendLoading} 
          />
        </div>
      </div>

      {/* Abschnitt 1: Abbrüche vor Anreise */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Abbrüche vor Anreise</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <ReasonListWidget 
              reasonsData={(reasonsData?.data || []).filter((r: any) => [
                "BK - ohne Grund abgesagt",
                "BK - hat besseres Jobangebot erhalten",
                "BK - hat Verletzung",
                "BK - hat Notfall in eigener Familie",
                "BK - hat Arzttermin",
                "BK - ist nicht in den Bus gestiegen Grund unbekannt",
                "BK - ist nicht in den Bus gestiegen Grund Alkoholmissbrauch"
              ].includes(r.reason))} 
              isLoading={isReasonsLoading} 
              eventType="cancelled_before_arrival"
            />
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <CancellationLeadTimeWidget 
              data={cancellationLeadTimeData?.data || []} 
              isLoading={isCancellationLeadTimeLoading} 
            />
          </div>
        </div>
      </div>

      {/* Abschnitt 2: Vorzeitige Abreisen nach Anreise */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Vorzeitige Abreisen nach Anreise</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <InstantDepartureWidget 
              data={overviewData?.data || []} 
              isLoading={isOverviewLoading} 
              detailedData={instantDeparturesData?.data || []}
            />
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <ReasonListWidget 
              reasonsData={(reasonsData?.data || []).filter((r: any) => [
                "BK - Deutschkenntnisse zu schlecht",
                "BK - Pflegefähigkeiten zu schlecht - Transfer",
                "BK- Pflegefähigkeiten zu schlecht - Grundpflege",
                "BK - Falsch informiert worden über Anforderungen der Stelle",
                "BK - zu wenig Einsatzbereitschaft/zu faul",
                "BK - Alkoholkonsum",
                "BK - Diebstahl",
                "BK - Drogen",
                "BK - Fühlt sich unwohl",
                "BK - Abreise aus sonstigen Gründen",
                "BK - Abreise aus privaten Gründen",
                "BK - eigenständig abgereist ohne Absprache"
              ].includes(r.reason))} 
              isLoading={isReasonsLoading} 
              eventType="shortened_after_arrival"
            />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <TimeAnalysisWidget 
              data={overviewData?.data || []} 
              isLoading={isOverviewLoading} 
              eventType="shortened_after_arrival"
              title="Verkürzungsdauer-Analyse"
            />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <CustomerSatisfactionWidget 
              data={satisfactionData?.data || []} 
              isLoading={isSatisfactionLoading} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProblematicStaysPage; 