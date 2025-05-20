import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import axios from 'axios';

import InstantDepartureWidget from '../components/problematic_stays/InstantDepartureWidget';
import CustomerSatisfactionWidget from '../components/problematic_stays/CustomerSatisfactionWidget';
import TrendAnalysisWidget from '../components/problematic_stays/TrendAnalysisWidget';
import OverviewWidget from '../components/problematic_stays/OverviewWidget';
import DistributionWidget from '../components/problematic_stays/DistributionWidget';
import CancellationLeadTimeWidget from '../components/problematic_stays/CancellationLeadTimeWidget';
import ReasonListWidget from '../components/problematic_stays/ReasonListWidget';
import TimeAnalysisWidget from '../components/problematic_stays/TimeAnalysisWidget';

import AgencySelector from '../components/common/AgencySelector';

const ProblematicStaysPage: React.FC = () => {
  const { timePeriod, selectedAgency, setActiveTab } = useAppStore();
  
  // State für die verschiedenen Daten
  const [overviewData, setOverviewData] = useState<any[]>([]);
  const [reasonsData, setReasonsData] = useState<any[]>([]);
  const [timeAnalysisData, setTimeAnalysisData] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [instantDeparturesData, setInstantDeparturesData] = useState<any[]>([]);
  const [replacementData, setReplacementData] = useState<any[]>([]);
  const [satisfactionData, setSatisfactionData] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [cancellationLeadTimeData, setCancellationLeadTimeData] = useState<any[]>([]);
  
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
      // Seite als "wird geladen" markieren
      setIsPageLoading(true);
      setLoadingProgress(0);
      
      const agencyId = selectedAgency ? selectedAgency.agency_id : null;
      
      try {
        // Alle Anfragen parallel starten anstatt sequentiell
        const requests = [
          // Übersichtsdaten
          {
            request: axios.get('/api/problematic_stays/overview', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setOverviewData,
            setLoading: setIsOverviewLoading
          },
          // Gründe
          {
            request: axios.get('/api/problematic_stays/reasons', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setReasonsData,
            setLoading: setIsReasonsLoading
          },
          // Zeitliche Analyse
          {
            request: axios.get('/api/problematic_stays/time-analysis', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setTimeAnalysisData,
            setLoading: setIsTimeAnalysisLoading
          },
          // Heatmap-Daten
          {
            request: axios.get('/api/problematic_stays/heatmap', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setHeatmapData,
            setLoading: setIsHeatmapLoading
          },
          // Instant Departures
          {
            request: axios.get('/api/problematic_stays/instant-departures', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setInstantDeparturesData,
            setLoading: setIsInstantDeparturesLoading
          },
          // Ersatz-Analyse
          {
            request: axios.get('/api/problematic_stays/replacement-analysis', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setReplacementData,
            setLoading: setIsReplacementLoading
          },
          // Kundenzufriedenheit
          {
            request: axios.get('/api/problematic_stays/customer-satisfaction', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
            setData: setSatisfactionData,
            setLoading: setIsSatisfactionLoading
          },
          // Trend-Analyse (immer letztes Jahr)
          {
            request: axios.get('/api/problematic_stays/trend-analysis', {
              params: { agency_id: agencyId, time_period: 'last_year' }
            }),
            setData: setTrendData,
            setLoading: setIsTrendLoading
          },
          // Abbrüche - Vorlaufzeit
          {
            request: axios.get('/api/problematic_stays/cancellation-lead-time', {
              params: { agency_id: agencyId, time_period: timePeriod }
            }),
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
              const response = await item.request;
              item.setData(response.data.data);
              item.setLoading(false);
              
              // Fortschritt aktualisieren
              completedRequests++;
              setLoadingProgress(Math.round((completedRequests / totalRequests) * 100));
            } catch (error) {
              console.error(`Fehler beim Laden (${index}):`, error);
              item.setLoading(false);
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
  }, [selectedAgency, timePeriod]);

  // Gesamtzahl der Einsätze extrahieren
  const totalCareStays = overviewData && overviewData.length > 0 ? overviewData[0].total_carestays : 0;
  const totalProblematic = overviewData && overviewData.length > 0 ? overviewData[0].total_problematic : 0;
  const problematicPercentage = overviewData && overviewData.length > 0 ? overviewData[0].problematic_percentage : 0;

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
      {!isOverviewLoading && overviewData.length > 0 && (
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
            data={overviewData} 
            isLoading={isOverviewLoading} 
          />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <DistributionWidget 
            data={overviewData} 
            isLoading={isOverviewLoading} 
          />
        </div>
      </div>

      {/* Zeitliche Entwicklung */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Problematische Einsätze - Zeitliche Entwicklung</h2>
          <TrendAnalysisWidget 
            data={trendData} 
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
              reasonsData={reasonsData.filter(r => [
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
              data={cancellationLeadTimeData} 
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
              data={overviewData} 
              isLoading={isOverviewLoading} 
              detailedData={instantDeparturesData}
            />
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <ReasonListWidget 
              reasonsData={reasonsData.filter(r => [
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
              data={timeAnalysisData} 
              isLoading={isTimeAnalysisLoading} 
              eventType="shortened_after_arrival"
              title="Verkürzungsdauer-Analyse"
            />
          </div>
        </div>
        <div className="grid grid-cols-1 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <CustomerSatisfactionWidget 
              data={satisfactionData} 
              isLoading={isSatisfactionLoading} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProblematicStaysPage; 