import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import ExportButton from '../components/common/ExportButton';
import TimeFilter from '../components/common/TimeFilter';
import OverviewWidget from '../components/problematic_stays/OverviewWidget';
import DistributionWidget from '../components/problematic_stays/DistributionWidget';
import TimeAnalysisWidget from '../components/problematic_stays/TimeAnalysisWidget';
import InstantDepartureWidget from '../components/problematic_stays/InstantDepartureWidget';

const StrengthWeaknessPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [overviewData, setOverviewData] = useState<any>(null);
  const [reasonsData, setReasonsData] = useState<any>(null);
  const [timeAnalysisData, setTimeAnalysisData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch overview data
        try {
          const overviewResponse = await apiService.getProblematicStaysOverview(selectedAgency.agency_id, timePeriod);
          setOverviewData(overviewResponse);
        } catch (err) {
          console.error('Error fetching problematic stays overview:', err);
        }
        
        // Fetch reasons data
        try {
          const reasonsResponse = await apiService.getProblematicStaysReasons(selectedAgency.agency_id, undefined, timePeriod);
          setReasonsData(reasonsResponse);
        } catch (err) {
          console.error('Error fetching problematic stays reasons:', err);
        }
        
        // Fetch time analysis data
        try {
          const timeAnalysisResponse = await apiService.getProblematicStaysTimeAnalysis(selectedAgency.agency_id, undefined, undefined, timePeriod);
          setTimeAnalysisData(timeAnalysisResponse);
        } catch (err) {
          console.error('Error fetching problematic stays time analysis:', err);
        }
        
      } catch (err) {
        console.error('Error fetching strength weakness analysis data:', err);
        setError('Fehler beim Laden der Daten. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  if (isLoading) {
    return <Loading message="Analyse-Daten werden geladen..." />;
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

  // Prüfen, ob Daten vorhanden sind
  const hasData = overviewData && overviewData.data && overviewData.data.length > 0;

  return (
    <div className="strength-weakness-page">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Stärken/Schwächen-Analyse: {selectedAgency.agency_name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Detaillierte Analyse von problematischen Pflegeeinsätzen
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <TimeFilter />
          <ExportButton 
            targetElementId="strength-weakness-content" 
            filename="staerken-schwaechen-analyse" 
            pageTitle="Stärken/Schwächen-Analyse" 
          />
        </div>
      </div>

      {!hasData ? (
        <div className="text-center p-8 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Keine Daten vorhanden</h2>
          <p className="text-gray-600 dark:text-gray-300">
            Für diese Agentur sind leider keine Daten zu problematischen Einsätzen im ausgewählten Zeitraum vorhanden.
          </p>
        </div>
      ) : (
        <div id="strength-weakness-content" className="print-container">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Übersicht der problematischen Einsätze</h2>
            
            {/* Hauptstatistik-Widget */}
            <OverviewWidget data={overviewData.data} isLoading={isLoading} />
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Verteilung nach Problemtyp und Einsatztyp</h2>
            
            {/* Verteilungs-Widget */}
            <DistributionWidget data={overviewData.data} isLoading={isLoading} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <TimeAnalysisWidget 
                data={timeAnalysisData?.data || []} 
                isLoading={isLoading} 
                eventType="cancelled_before_arrival"
                title="Vorlaufzeit bei Abbrüchen"
              />
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <TimeAnalysisWidget 
                data={timeAnalysisData?.data || []} 
                isLoading={isLoading} 
                eventType="shortened_after_arrival"
                title="Verkürzungsdauer-Analyse"
              />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <InstantDepartureWidget 
              data={overviewData.data} 
              isLoading={isLoading}
            />
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Analyse der Abbruch- und Beendigungsgründe</h2>
            
            {/* Hier wird später die Analyse der Gründe platziert */}
            <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg text-center">
              <p className="text-gray-600 dark:text-gray-300">
                Gründe-Analyse wird geladen...
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Zeitliche Entwicklung</h2>
            
            {/* Hier wird später die zeitliche Analyse platziert */}
            <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg text-center">
              <p className="text-gray-600 dark:text-gray-300">
                Zeitliche Analyse wird geladen...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrengthWeaknessPage; 