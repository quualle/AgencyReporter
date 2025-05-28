import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Loading from '../common/Loading';
import ErrorMessage from '../common/ErrorMessage';

const API_URL = process.env.REACT_APP_API_URL || '/api';

interface ConfirmedCareStaysData {
  time_period: string;
  total_confirmed_stays: number;
  agency_count: number;
  agencies: {
    agency_id: string;
    agency_name: string;
    confirmed_stays_count: number;
    rank_by_count: number;
  }[];
}

interface ConfirmedCareStaysWidgetProps {
  timePeriod: string;
}

const ConfirmedCareStaysWidget: React.FC<ConfirmedCareStaysWidgetProps> = ({ timePeriod }) => {
  const [data, setData] = useState<ConfirmedCareStaysData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(`${API_URL}/care_stays/confirmed`, {
          params: { time_period: timePeriod }
        });
        setData(response.data);
      } catch (err) {
        setError('Fehler beim Laden der bestätigten Einsätze');
        console.error('Error fetching confirmed care stays:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timePeriod]);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <Loading />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <ErrorMessage message={error || 'Keine Daten verfügbar'} />
      </div>
    );
  }

  // Top 5 Agenturen
  const topAgencies = data.agencies.slice(0, 5);
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          🏢 Bestätigte Einsätze
        </h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          {showDetails ? 'Weniger' : 'Mehr'} anzeigen
        </button>
      </div>

      {/* Gesamtübersicht */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {data.total_confirmed_stays.toLocaleString('de-DE')}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Bestätigte Einsätze gesamt
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-semibold text-gray-700 dark:text-gray-300">
              {data.agency_count}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Agenturen
            </p>
          </div>
        </div>
      </div>

      {/* Top 5 Agenturen */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
          🏆 Top 5 Agenturen
        </h4>
        
        {topAgencies.map((agency, index) => {
          const percentage = (agency.confirmed_stays_count / data.total_confirmed_stays) * 100;
          
          return (
            <div key={agency.agency_id} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-semibold ${
                    index === 0 ? 'text-yellow-600' :
                    index === 1 ? 'text-gray-600' :
                    index === 2 ? 'text-orange-600' :
                    'text-gray-600'
                  }`}>
                    #{agency.rank_by_count}
                  </span>
                  <span className="text-sm text-gray-900 dark:text-white">
                    {agency.agency_name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    {agency.confirmed_stays_count.toLocaleString('de-DE')}
                  </span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    ({percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-orange-500' :
                    'bg-blue-500'
                  }`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Erweiterte Details */}
      {showDetails && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Alle Agenturen ({data.agency_count})
          </h4>
          <div className="max-h-60 overflow-y-auto space-y-2">
            {data.agencies.map((agency) => (
              <div
                key={agency.agency_id}
                className="flex items-center justify-between py-1 text-sm"
              >
                <span className="text-gray-700 dark:text-gray-300">
                  <span className="font-medium">#{agency.rank_by_count}</span> {agency.agency_name}
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {agency.confirmed_stays_count.toLocaleString('de-DE')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfirmedCareStaysWidget;