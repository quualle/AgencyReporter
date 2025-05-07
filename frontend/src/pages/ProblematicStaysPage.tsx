import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import axios from 'axios';

import ReasonHeatmapWidget from '../components/problematic_stays/ReasonHeatmapWidget';
import InstantDepartureWidget from '../components/problematic_stays/InstantDepartureWidget';
import CustomerSatisfactionWidget from '../components/problematic_stays/CustomerSatisfactionWidget';
import TrendAnalysisWidget from '../components/problematic_stays/TrendAnalysisWidget';
import OverviewWidget from '../components/problematic_stays/OverviewWidget';
import DistributionWidget from '../components/problematic_stays/DistributionWidget';
import ReplacementAnalysisWidget from '../components/problematic_stays/ReplacementAnalysisWidget';
import FollowUpAnalysisWidget from '../components/problematic_stays/FollowUpAnalysisWidget';

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
  
  // Loading States
  const [isOverviewLoading, setIsOverviewLoading] = useState<boolean>(true);
  const [isReasonsLoading, setIsReasonsLoading] = useState<boolean>(true);
  const [isTimeAnalysisLoading, setIsTimeAnalysisLoading] = useState<boolean>(true);
  const [isHeatmapLoading, setIsHeatmapLoading] = useState<boolean>(true);
  const [isInstantDeparturesLoading, setIsInstantDeparturesLoading] = useState<boolean>(true);
  const [isReplacementLoading, setIsReplacementLoading] = useState<boolean>(true);
  const [isSatisfactionLoading, setIsSatisfactionLoading] = useState<boolean>(true);
  const [isTrendLoading, setIsTrendLoading] = useState<boolean>(true);

  // Tab-Zustand für aktiven Tab
  React.useEffect(() => {
    setActiveTab('problematic-stays');
  }, [setActiveTab]);

  // Daten laden
  useEffect(() => {
    const fetchData = async () => {
      try {
        const agencyId = selectedAgency ? selectedAgency.agency_id : null;
        
        // Übersichtsdaten laden
        setIsOverviewLoading(true);
        const overviewResponse = await axios.get('/api/problematic_stays/overview', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setOverviewData(overviewResponse.data.data);
        setIsOverviewLoading(false);

        // Gründe laden
        setIsReasonsLoading(true);
        const reasonsResponse = await axios.get('/api/problematic_stays/reasons', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setReasonsData(reasonsResponse.data.data);
        setIsReasonsLoading(false);

        // Zeitliche Analyse laden
        setIsTimeAnalysisLoading(true);
        const timeAnalysisResponse = await axios.get('/api/problematic_stays/time-analysis', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setTimeAnalysisData(timeAnalysisResponse.data.data);
        setIsTimeAnalysisLoading(false);

        // Heatmap-Daten laden
        setIsHeatmapLoading(true);
        const heatmapResponse = await axios.get('/api/problematic_stays/heatmap', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setHeatmapData(heatmapResponse.data.data);
        setIsHeatmapLoading(false);

        // Instant Departures laden
        setIsInstantDeparturesLoading(true);
        const instantDeparturesResponse = await axios.get('/api/problematic_stays/instant-departures', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setInstantDeparturesData(instantDeparturesResponse.data.data);
        setIsInstantDeparturesLoading(false);

        // Ersatz-Analyse laden
        setIsReplacementLoading(true);
        const replacementResponse = await axios.get('/api/problematic_stays/replacement-analysis', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setReplacementData(replacementResponse.data.data);
        setIsReplacementLoading(false);

        // Kundenzufriedenheit laden
        setIsSatisfactionLoading(true);
        const satisfactionResponse = await axios.get('/api/problematic_stays/customer-satisfaction', {
          params: {
            agency_id: agencyId,
            time_period: timePeriod
          }
        });
        setSatisfactionData(satisfactionResponse.data.data);
        setIsSatisfactionLoading(false);

        // Trend-Analyse laden
        setIsTrendLoading(true);
        const trendResponse = await axios.get('/api/problematic_stays/trend-analysis', {
          params: {
            agency_id: agencyId,
            time_period: 'last_year' // Für Trend immer letztes Jahr anzeigen
          }
        });
        setTrendData(trendResponse.data.data);
        setIsTrendLoading(false);
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error);
        setIsOverviewLoading(false);
        setIsReasonsLoading(false);
        setIsTimeAnalysisLoading(false);
        setIsHeatmapLoading(false);
        setIsInstantDeparturesLoading(false);
        setIsReplacementLoading(false);
        setIsSatisfactionLoading(false);
        setIsTrendLoading(false);
      }
    };

    fetchData();
  }, [selectedAgency, timePeriod]);

  // Gesamtzahl der Einsätze extrahieren
  const totalCareStays = overviewData && overviewData.length > 0 ? overviewData[0].total_carestays : 0;
  const totalProblematic = overviewData && overviewData.length > 0 ? overviewData[0].total_problematic : 0;
  const problematicPercentage = overviewData && overviewData.length > 0 ? overviewData[0].problematic_percentage : 0;

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

      <div className="mb-6">
        <AgencySelector />
      </div>

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

      {/* Heatmap und Customer Satisfaction */}
      <div className="grid grid-cols-1 lg:grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <ReasonHeatmapWidget 
            data={heatmapData} 
            isLoading={isHeatmapLoading} 
          />
        </div>
      </div>

      {/* Sofortige Abreisen - Einzelne Zeile mit voller Breite */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <InstantDepartureWidget 
            data={overviewData} 
            isLoading={isOverviewLoading} 
            detailedData={instantDeparturesData}
          />
        </div>
      </div>
      
      {/* Ersatz- und Folgeeinsatz-Analyse - Zwei Widgets nebeneinander */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <ReplacementAnalysisWidget 
            data={replacementData} 
            isLoading={isReplacementLoading} 
          />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <FollowUpAnalysisWidget 
            data={replacementData} 
            isLoading={isReplacementLoading} 
          />
        </div>
      </div>
      
      {/* Kundenzufriedenheit - Einzelne Zeile mit voller Breite */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <CustomerSatisfactionWidget 
            data={satisfactionData} 
            isLoading={isSatisfactionLoading} 
          />
        </div>
      </div>

      {/* Trend-Analyse */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <TrendAnalysisWidget 
            data={trendData} 
            isLoading={isTrendLoading} 
          />
        </div>
      </div>
    </div>
  );
};

export default ProblematicStaysPage; 