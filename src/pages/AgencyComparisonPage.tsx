import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import axios from 'axios';
import ExportButton from '../components/common/ExportButton';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import TimeFilter from '../components/common/TimeFilter';

// Will create these components next
import TopBottomAgenciesWidget from '../components/agency_comparison/TopBottomAgenciesWidget';
import AverageCarestayWidget from '../components/agency_comparison/AverageCarestayWidget';
import AverageContractDurationWidget from '../components/agency_comparison/AverageContractDurationWidget';
import ProblematicStaysRatioWidget from '../components/agency_comparison/ProblematicStaysRatioWidget';

const AgencyComparisonPage: React.FC = () => {
  const { timePeriod, setActiveTab } = useAppStore();
  
  // State for the different data sets
  const [topBottomAgenciesData, setTopBottomAgenciesData] = useState<any[]>([]);
  const [averageCarestayData, setAverageCarestayData] = useState<any[]>([]);
  const [averageContractDurationData, setAverageContractDurationData] = useState<any[]>([]);
  const [problematicStaysRatioData, setProblematicStaysRatioData] = useState<any[]>([]);
  
  // Loading states
  const [isTopBottomLoading, setIsTopBottomLoading] = useState<boolean>(true);
  const [isAverageCarestayLoading, setIsAverageCarestayLoading] = useState<boolean>(true);
  const [isAverageContractDurationLoading, setIsAverageContractDurationLoading] = useState<boolean>(true);
  const [isProblematicStaysRatioLoading, setIsProblematicStaysRatioLoading] = useState<boolean>(true);
  
  // Overall page loading state
  const [isPageLoading, setIsPageLoading] = useState<boolean>(true);
  // Loading progress in percentage
  const [loadingProgress, setLoadingProgress] = useState<number>(0);

  // Set active tab
  React.useEffect(() => {
    setActiveTab('agency-comparison');
  }, [setActiveTab]);

  // Load data
  useEffect(() => {
    const fetchData = async () => {
      // Mark page as loading
      setIsPageLoading(true);
      setLoadingProgress(0);
      
      try {
        // Start all requests in parallel
        const requests = [
          // Top/Bottom agencies by deployment days
          {
            request: axios.get('/api/agencies/ranking/deployment-days', {
              params: { time_period: timePeriod }
            }),
            setData: setTopBottomAgenciesData,
            setLoading: setIsTopBottomLoading
          },
          // Average carestay duration per agency
          {
            request: axios.get('/api/agencies/comparison/average-carestay', {
              params: { time_period: timePeriod }
            }),
            setData: setAverageCarestayData,
            setLoading: setIsAverageCarestayLoading
          },
          // Average contract duration per agency
          {
            request: axios.get('/api/agencies/comparison/average-contract-duration', {
              params: { time_period: timePeriod }
            }),
            setData: setAverageContractDurationData,
            setLoading: setIsAverageContractDurationLoading
          },
          // Problematic stays ratio per agency
          {
            request: axios.get('/api/problematic_stays/ratio-by-agency', {
              params: { time_period: timePeriod }
            }),
            setData: setProblematicStaysRatioData,
            setLoading: setIsProblematicStaysRatioLoading
          }
        ];
        
        // Set all loading states to true
        requests.forEach(item => item.setLoading(true));
        
        // Track progress
        let completedRequests = 0;
        const totalRequests = requests.length;
        
        // Execute in parallel
        await Promise.all(
          requests.map(async (item, index) => {
            try {
              const response = await item.request;
              item.setData(response.data.data);
              item.setLoading(false);
              
              // Update progress
              completedRequests++;
              setLoadingProgress(Math.round((completedRequests / totalRequests) * 100));
            } catch (error) {
              console.error(`Error loading data (${index}):`, error);
              item.setLoading(false);
              
              // Provide empty data to prevent UI crashes
              if (index === 0) setTopBottomAgenciesData([]);
              if (index === 1) setAverageCarestayData([]);
              if (index === 2) setAverageContractDurationData([]);
              if (index === 3) setProblematicStaysRatioData([]);
            }
          })
        );
        
        // Mark page as loaded
        setIsPageLoading(false);
      } catch (error) {
        console.error('Error loading data:', error);
        // End loading on error
        setIsTopBottomLoading(false);
        setIsAverageCarestayLoading(false);
        setIsAverageContractDurationLoading(false);
        setIsProblematicStaysRatioLoading(false);
        setIsPageLoading(false);
      }
    };

    fetchData();
  }, [timePeriod]);

  // Show loading overlay while data is being loaded
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
              Bitte haben Sie einen Moment Geduld, während wir die Vergleichsdaten für die Agenturen vorbereiten.
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Agenturvergleich - Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Übersicht und Benchmarking der Agenturen im Vergleich.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Agenturvergleich - Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Übersicht und Benchmarking der Agenturen im Vergleich.
          </p>
        </div>
        <div className="flex space-x-4">
          <TimeFilter />
          <ExportButton 
            targetElementId="agency-comparison-content" 
            filename="agenturvergleich" 
            pageTitle="Agenturvergleich Dashboard" 
          />
        </div>
      </div>

      <div id="agency-comparison-content" className="print-container">
        {/* Top/Bottom Agencies by Deployment Days */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Top-Agenturen: Einsatztage</h2>
            <TopBottomAgenciesWidget 
              data={topBottomAgenciesData} 
              isLoading={isTopBottomLoading}
              showTop={true}
              limit={5}
            />
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Flop-Agenturen: Einsatztage</h2>
            <TopBottomAgenciesWidget 
              data={topBottomAgenciesData} 
              isLoading={isTopBottomLoading}
              showTop={false}
              limit={5}
            />
          </div>
        </div>

        {/* Average Carestay Duration */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Durchschnittliche Einsatzdauer (Carestay)</h2>
          <AverageCarestayWidget 
            data={averageCarestayData} 
            isLoading={isAverageCarestayLoading} 
          />
        </div>

        {/* Average Contract Duration */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Durchschnittliche Vertragsdauer</h2>
          <AverageContractDurationWidget 
            data={averageContractDurationData} 
            isLoading={isAverageContractDurationLoading} 
          />
        </div>

        {/* Problematic Stays Ratio */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Top/Flop: Anteil problematischer Einsätze</h2>
          <ProblematicStaysRatioWidget 
            data={problematicStaysRatioData} 
            isLoading={isProblematicStaysRatioLoading} 
          />
        </div>
      </div>
    </div>
  );
};

export default AgencyComparisonPage; 