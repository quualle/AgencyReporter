import React, { useState, useEffect } from 'react';
import { databaseCacheService } from '../../services/api';

interface CacheStatsProps {
  agencyId?: string;
  showDetails?: boolean;
}

interface CacheStatsData {
  total_entries: number;
  preloaded_entries: number;
  expired_entries: number;
  recent_sessions_24h: number;
  database_info: {
    size_mb: number;
    cached_data_count: number;
    preload_sessions_count: number;
    data_freshness_count: number;
  };
}

interface FreshnessData {
  all_data_fresh: boolean;
  freshness_details: Record<string, Record<string, any>>;
  stale_data_types: Array<{
    data_type: string;
    time_period: string;
  }>;
}

const CacheStats: React.FC<CacheStatsProps> = ({ agencyId, showDetails = false }) => {
  const [stats, setStats] = useState<CacheStatsData | null>(null);
  const [freshness, setFreshness] = useState<FreshnessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch cache stats
        const statsData = await databaseCacheService.getCacheStats();
        setStats(statsData);

        // Fetch freshness data if agency ID is provided
        if (agencyId) {
          const freshnessData = await databaseCacheService.checkDataFreshness(agencyId);
          setFreshness(freshnessData);
        }

      } catch (err) {
        console.error('Error fetching cache data:', err);
        setError('Fehler beim Laden der Cache-Statistiken');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Reduced polling to 60 seconds to prevent excessive re-renders
    const interval = setInterval(fetchData, 60000);
    
    return () => clearInterval(interval);
  }, [agencyId]);

  if (loading) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-4 border border-blue-200 dark:border-gray-600">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800 dark:text-white flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          Cache Status
        </h3>
        {freshness && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            freshness.all_data_fresh 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {freshness.all_data_fresh ? 'Aktuell' : 'Teilweise veraltet'}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Einträge:</span>
            <span className="font-medium text-gray-800 dark:text-white">{stats.total_entries}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Preloaded:</span>
            <span className="font-medium text-gray-800 dark:text-white">{stats.preloaded_entries}</span>
          </div>
        </div>
        
        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Sessions 24h:</span>
            <span className="font-medium text-gray-800 dark:text-white">{stats.recent_sessions_24h}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">DB Größe:</span>
            <span className="font-medium text-gray-800 dark:text-white">{stats.database_info?.size_mb?.toFixed(2) || 'N/A'} MB</span>
          </div>
        </div>
      </div>

      {showDetails && freshness && (
        <div className="mt-4 pt-3 border-t border-blue-200 dark:border-gray-600">
          <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Datenaktualität</h4>
          <div className="space-y-1">
            {Object.entries(freshness.freshness_details || {}).map(([dataType, periods]) => (
              <div key={dataType} className="text-xs">
                <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">{dataType}:</span>
                <div className="ml-2 flex flex-wrap gap-1">
                  {Object.entries(periods as Record<string, any>).map(([period, data]) => (
                    <span 
                      key={period}
                      className={`px-1 py-0.5 rounded text-xs ${
                        data.is_fresh 
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                      }`}
                    >
                      {period}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {freshness.stale_data_types && freshness.stale_data_types.length > 0 && (
            <div className="mt-2">
              <h5 className="text-xs font-medium text-orange-600 dark:text-orange-400">Veraltete Daten:</h5>
              <div className="flex flex-wrap gap-1 mt-1">
                {freshness.stale_data_types.map((stale, index) => (
                  <span 
                    key={index}
                    className="px-1 py-0.5 bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300 rounded text-xs"
                  >
                    {stale.data_type}/{stale.time_period}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CacheStats;