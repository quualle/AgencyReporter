import React, { useState, useEffect, useCallback } from 'react';
import { useAppStore } from '../store/appStore';
import TimeFilter from '../components/common/TimeFilter';
import AgencyRankingList, { AgencyData } from '../components/common/AgencyRankingList';
import AgencySelector from '../components/common/AgencySelector';
import ExportButton from '../components/common/ExportButton';
import ProblematicStaysHeatmap from '../components/common/ProblematicStaysHeatmap';
import MarketShareTreemap from '../components/common/MarketShareTreemap';
import apiService from '../services/api';

// Interface for API response data
interface AgencyDataResponse {
  agency_id: string;
  agency_name: string;
  total_carestays: number;
  total_problematic: number;
  problematic_percentage: number;
  avg_stay_duration_days?: number;
  cancelled_before_arrival_count?: number;
  shortened_after_arrival_count?: number;
  cancelled_percentage?: number;
  shortened_percentage?: number;
  [key: string]: any;
}

const AgencyComparisonPage: React.FC = () => {
  const { timePeriod, setActiveTab, selectedAgency, setSelectedAgency } = useAppStore();

  // State for agencies data
  const [agenciesData, setAgenciesData] = useState<AgencyDataResponse[]>([]);
  const [loadingState, setLoadingState] = useState<{
    overview: boolean;
    reactionTimes: boolean;
    profileQuality: boolean;
    heatmap: boolean;
  }>({
    overview: true,
    reactionTimes: true,
    profileQuality: true,
    heatmap: true
  });
  const [error, setError] = useState<string | null>(null);
  const [reactionTimesData, setReactionTimesData] = useState<any[]>([]);
  const [profileQualityData, setProfileQualityData] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);

  // Computed loading state for UI
  const isLoading = Object.values(loadingState).some(value => value === true);

  // Set active tab
  useEffect(() => {
    setActiveTab('agency-comparison');
  }, [setActiveTab]);

  // Fetch data function with progressive loading
  const fetchData = useCallback(async (forceRefresh: boolean = false) => {
    // Initialize loading states
    setLoadingState({
      overview: true,
      reactionTimes: true,
      profileQuality: true,
      heatmap: true
    });
    setError(null);

    try {
      // Use the new batch data fetching API
      const result = await apiService.getAgencyComparisonData(timePeriod, forceRefresh);
      
      // Check for errors
      if (result.error) {
        throw new Error('Server returned an error');
      }

      // Update state progressively as data becomes available
      if (result.problematicStaysOverview && result.problematicStaysOverview.data) {
        setAgenciesData(result.problematicStaysOverview.data);
        setLoadingState(prev => ({ ...prev, overview: false }));
      }
      
      if (result.reactionTimes && result.reactionTimes.data) {
        setReactionTimesData(result.reactionTimes.data);
        setLoadingState(prev => ({ ...prev, reactionTimes: false }));
      }
      
      if (result.profileQuality && result.profileQuality.data) {
        setProfileQualityData(result.profileQuality.data);
        setLoadingState(prev => ({ ...prev, profileQuality: false }));
      }
      
      if (result.problematicStaysHeatmap && result.problematicStaysHeatmap.data) {
        setHeatmapData(result.problematicStaysHeatmap.data);
        setLoadingState(prev => ({ ...prev, heatmap: false }));
      }
    } catch (err) {
      console.error('Error fetching agency comparison data:', err);
      setError('Fehler beim Laden der Daten. Bitte versuche es später erneut.');
      // Reset data
      setAgenciesData([]);
      setReactionTimesData([]);
      setProfileQualityData([]);
      setHeatmapData([]);
      // Reset loading states
      setLoadingState({
        overview: false,
        reactionTimes: false,
        profileQuality: false,
        heatmap: false
      });
    }
  }, [timePeriod]);

  // Fetch data when time period changes
  useEffect(() => {
    fetchData();
  }, [fetchData, timePeriod]);

  // Handle agency selection
  const handleAgencyClick = (agencyId: string, agencyName: string) => {
    setSelectedAgency({
      agency_id: agencyId,
      agency_name: agencyName
    });
  };

  // Format percentage values
  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Format duration values
  const formatDuration = (value: number) => {
    return `${value.toFixed(1)} Tage`;
  };

  // Convert data to the right format for ranking lists
  const getProblematicStaysData = (): AgencyData[] => {
    return agenciesData.map(agency => ({
      agency_id: agency.agency_id,
      agency_name: agency.agency_name,
      value: agency.problematic_percentage,
      total_count: agency.total_carestays
    }));
  };

  const getCancelledBeforeArrivalData = (): AgencyData[] => {
    return agenciesData.map(agency => ({
      agency_id: agency.agency_id,
      agency_name: agency.agency_name,
      value: agency.cancelled_percentage || 0,
      total_count: agency.cancelled_before_arrival_count
    }));
  };

  const getShortenedAfterArrivalData = (): AgencyData[] => {
    return agenciesData.map(agency => ({
      agency_id: agency.agency_id,
      agency_name: agency.agency_name,
      value: agency.shortened_percentage || 0,
      total_count: agency.shortened_after_arrival_count
    }));
  };

  const getTotalCareStaysData = (): AgencyData[] => {
    return agenciesData.map(agency => ({
      agency_id: agency.agency_id,
      agency_name: agency.agency_name,
      value: agency.total_carestays,
      total_count: agency.total_carestays
    }));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Strategisches Agentur-Benchmarking
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Vergleichsanalyse aller Agenturen nach Leistungsindikatoren und Problemmetriken
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-between mb-6 gap-4">
        <TimeFilter />
        <div className="flex items-center gap-4">
          <div className="w-64">
            <AgencySelector />
          </div>
          <button 
            onClick={() => fetchData(true)} 
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md flex items-center"
            disabled={isLoading}
          >
            <svg className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {isLoading ? 'Wird geladen...' : 'Aktualisieren'}
          </button>
          <ExportButton targetElementId="agency-comparison-content" filename="agentur-benchmarking" pageTitle="Strategisches Agentur-Benchmarking" />
        </div>
      </div>
      
      {/* Progress indicator for progressive loading */}
      {isLoading && (
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col space-y-2">
            <h3 className="text-gray-700 dark:text-gray-300 font-medium mb-2">Daten werden geladen...</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className={`w-4 h-4 mr-2 rounded-full ${loadingState.overview ? 'bg-gray-300 dark:bg-gray-600' : 'bg-green-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Übersichtsdaten</span>
              </div>
              <div className="flex items-center">
                <div className={`w-4 h-4 mr-2 rounded-full ${loadingState.reactionTimes ? 'bg-gray-300 dark:bg-gray-600' : 'bg-green-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Reaktionszeiten</span>
              </div>
              <div className="flex items-center">
                <div className={`w-4 h-4 mr-2 rounded-full ${loadingState.profileQuality ? 'bg-gray-300 dark:bg-gray-600' : 'bg-green-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Profilqualität</span>
              </div>
              <div className="flex items-center">
                <div className={`w-4 h-4 mr-2 rounded-full ${loadingState.heatmap ? 'bg-gray-300 dark:bg-gray-600' : 'bg-green-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Problemverteilung</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg mb-6 border border-indigo-100 dark:border-indigo-800">
        <h2 className="text-lg font-semibold text-indigo-700 dark:text-indigo-300 mb-2">Strategische Insights</h2>
        <p className="text-indigo-600 dark:text-indigo-400">
          Die Vergleichsanalyse ermöglicht die Identifikation von Best Practices und Optimierungspotenzialen. Klicken Sie auf eine Agentur, um deren Detaildaten einzusehen.
        </p>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      <div id="agency-comparison-content" className="space-y-8">
        {/* Volumen-Sektion */}
        <div className="mb-2">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
            1. Agentur-Volumen und Marktanteile
          </h2>
          <div className="grid grid-cols-1 gap-6 mb-6">
            <MarketShareTreemap 
              data={agenciesData}
              isLoading={loadingState.overview}
              onAgencyClick={handleAgencyClick}
            />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgencyRankingList
              title="Marktführer nach Einsatzvolumen"
              agencies={getTotalCareStaysData()}
              metric="total_carestays"
              formatValue={(value) => value.toLocaleString()}
              isLoading={isLoading}
              type="top"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Anzahl"
            />
          </div>
        </div>

        {/* Qualitäts-/Erfolgsmetriken */}
        <div className="mb-2">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
            2. Erfolgsquoten und Qualitätsmetriken
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgencyRankingList
              title="Best Performer: Niedrigste Rate problematischer Einsätze"
              agencies={getProblematicStaysData()}
              metric="problematic_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="bottom"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Einsätze"
            />
            
            <AgencyRankingList
              title="Optimierungspotential: Höchste Rate problematischer Einsätze"
              agencies={getProblematicStaysData()}
              metric="problematic_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="top"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Einsätze"
            />
          </div>
        </div>

        {/* Heatmap für die Problemverteilung */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
            3. Problemverteilung nach Agentur und Kategorie
          </h2>
          <div className="mb-6">
            <ProblematicStaysHeatmap 
              data={heatmapData} 
              isLoading={loadingState.heatmap}
              onAgencyClick={handleAgencyClick}
            />
          </div>
        </div>
        
        {/* Detailanalyse der Probleme */}
        <div className="mb-2">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 border-b border-gray-200 dark:border-gray-700 pb-2">
            4. Detailanalyse nach Problemkategorien
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <AgencyRankingList
              title="Vor-Anreise-Risiken: Höchste Rate Abbrüche vor Anreise"
              agencies={getCancelledBeforeArrivalData()}
              metric="cancelled_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="top"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Anzahl"
            />
            
            <AgencyRankingList
              title="Best Practice: Niedrigste Rate Abbrüche vor Anreise"
              agencies={getCancelledBeforeArrivalData()}
              metric="cancelled_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="bottom"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Anzahl"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgencyRankingList
              title="Kundenzufriedenheitsrisiko: Höchste Rate vorzeitiger Beendigungen"
              agencies={getShortenedAfterArrivalData()}
              metric="shortened_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="top"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Anzahl"
            />
            
            <AgencyRankingList
              title="Best Practice: Niedrigste Rate vorzeitiger Beendigungen"
              agencies={getShortenedAfterArrivalData()}
              metric="shortened_percentage"
              formatValue={formatPercentage}
              showTotal={true}
              isLoading={isLoading}
              type="bottom"
              limit={100}
              onAgencyClick={handleAgencyClick}
              valueLabel="Rate"
              totalLabel="Anzahl"
            />
          </div>
        </div>
        
        {/* Strategische Empfehlungen */}
        <div className="bg-green-50 dark:bg-green-900/20 p-5 rounded-lg border border-green-100 dark:border-green-800 mb-4">
          <h2 className="text-lg font-semibold text-green-700 dark:text-green-300 mb-2">Strategische Empfehlungen</h2>
          <ul className="list-disc list-inside space-y-2 text-green-600 dark:text-green-400">
            <li>Best Practices von Agenturen mit niedrigen Problemraten analysieren und dokumentieren</li>
            <li>Agenturen mit hohen Problemraten gezielt schulen und unterstützen</li>
            <li>Abbruchgründe vor Anreise und vorzeitige Beendigungen detailliert auswerten</li>
            <li>Trainingsmaßnahmen für Agenturen mit hohen Problemraten entwickeln</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AgencyComparisonPage;