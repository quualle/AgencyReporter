import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import apiService from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import ExportButton from '../components/common/ExportButton';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [kpiData, setKpiData] = useState<any>(null);
  const [responseTimeData, setResponseTimeData] = useState<any>(null);
  const [profileData, setProfileData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch data in parallel, but handle each API call separately to prevent complete failure
        try {
          const kpiResponse = await apiService.getAgencyQuotas(selectedAgency.agency_id, timePeriod);
          setKpiData(kpiResponse);
        } catch (err) {
          console.error('Error fetching KPI data:', err);
          // Setze Standard-KPI-Daten
        }
        
        try {
          const responseTimeResponse = await apiService.getAgencyReactionTimes(selectedAgency.agency_id, timePeriod);
          setResponseTimeData(responseTimeResponse);
        } catch (err) {
          console.error('Error fetching response time data:', err);
          // Setze Standard-Reaktionszeit-Daten
        }
        
        try {
          const profileResponse = await apiService.getAgencyProfileQuality(selectedAgency.agency_id, timePeriod);
          setProfileData(profileResponse);
        } catch (err) {
          console.error('Error fetching profile quality data:', err);
          // Standard-Profildaten werden bereits vom API-Service bereitgestellt
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Fehler beim Laden der Daten. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const handleCardClick = (route: string) => {
    navigate(route);
  };

  if (isLoading) {
    return <Loading message="Dashboard-Daten werden geladen..." />;
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
    <div className="dashboard">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Dashboard: {selectedAgency.agency_name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Übersicht der wichtigsten Kennzahlen
          </p>
        </div>
        <ExportButton 
          targetElementId="dashboard-content" 
          filename="dashboard" 
          pageTitle="Dashboard Übersicht" 
        />
      </div>

      <div id="dashboard-content" className="print-container">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* KPI Card */}
          <div
            className="dashboard-card cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            onClick={() => handleCardClick('/quotas')}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Quoten</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Reservierungsrate:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {kpiData?.reservation_rate ? `${(kpiData.reservation_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Erfüllungsrate:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {kpiData?.fulfillment_rate ? `${(kpiData.fulfillment_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Abbruchrate:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {kpiData?.cancellation_rate ? `${(kpiData.cancellation_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Response Times Card */}
          <div
            className="dashboard-card cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            onClick={() => handleCardClick('/response-times')}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Reaktionszeiten</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Bis zur Reservierung:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_reservation ? `${responseTimeData.avg_time_to_reservation.toFixed(1)} Std.` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Bis zum Personalvorschlag:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_proposal ? `${responseTimeData.avg_time_to_proposal.toFixed(1)} Std.` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Bis zum Abbruch:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {responseTimeData?.avg_time_to_cancellation ? `${responseTimeData.avg_time_to_cancellation.toFixed(1)} Std.` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Profile Quality Card */}
          <div
            className="dashboard-card cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            onClick={() => handleCardClick('/quality')}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Profilqualität</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Erfahrungs-Regelverstöße:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {profileData?.experience_violation_rate ? `${(profileData.experience_violation_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Sprachkenntnis-Regelverstöße:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {profileData?.language_violation_rate ? `${(profileData.language_violation_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Führerschein-Regelverstöße:</span>
                <span className="font-medium text-gray-800 dark:text-white">
                  {profileData?.license_violation_rate ? `${(profileData.license_violation_rate * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Strength/Weakness Analysis Card */}
          <div
            className="dashboard-card cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 md:col-span-2 lg:col-span-3"
            onClick={() => handleCardClick('/strength-weakness')}
          >
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Stärken- und Schwächenanalyse</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-2">
              Detaillierte Analyse der Stärken und Schwächen dieser Agentur im Vergleich zum Durchschnitt.
            </p>
            <div className="mt-4 text-center">
              <button
                className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  handleCardClick('/strength-weakness');
                }}
              >
                Zur Analyse
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 