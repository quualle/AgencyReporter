import React, { useState, useEffect } from 'react';
import { databaseCacheService } from '../../services/api';
import { useLocation } from 'react-router-dom';

interface CacheStatsProps {
  agencyId?: string;
  showDetails?: boolean;
  showCategories?: boolean; // Neue Option für kategorisierte Anzeige
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
  // Erweiterte Statistiken nach Kategorie
  category_stats?: {
    dashboard: {
      entries: number;
      fresh: number;
      stale: number;
    };
    agency_specific: {
      entries: number;
      fresh: number;
      stale: number;
    };
    overall: {
      entries: number;
      fresh: number;
      stale: number;
    };
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

const CacheStats: React.FC<CacheStatsProps> = ({ 
  agencyId, 
  showDetails = false,
  showCategories = true 
}) => {
  const [stats, setStats] = useState<CacheStatsData | null>(null);
  const [freshness, setFreshness] = useState<FreshnessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();

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

  // Bestimme die aktuelle Seite für Kontext
  const getCurrentPageContext = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path === '/quotas') return 'Quoten';
    if (path === '/response-times') return 'Reaktionszeiten';
    if (path === '/problematic-stays') return 'Problemeinsätze';
    return 'Andere';
  };

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

  const currentPage = getCurrentPageContext();

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-4 border border-blue-200 dark:border-gray-600">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800 dark:text-white flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          Cache Status
          <span className="text-xs font-normal text-gray-500 ml-2">({currentPage})</span>
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

      {/* Hauptstatistiken */}
      <div className="grid grid-cols-2 gap-3 text-sm mb-3">
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

      {/* Kategorisierte Cache-Anzeige */}
      {showCategories && stats.category_stats && (
        <div className="border-t border-blue-200 dark:border-gray-600 pt-3 mb-3">
          <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Cache-Kategorien</h4>
          <div className="space-y-2">
            {/* Dashboard Cache */}
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">Dashboard:</span>
              <div className="flex items-center gap-2">
                <span className="text-green-600 dark:text-green-400">
                  {stats.category_stats.dashboard.fresh} aktuell
                </span>
                {stats.category_stats.dashboard.stale > 0 && (
                  <span className="text-orange-600 dark:text-orange-400">
                    {stats.category_stats.dashboard.stale} veraltet
                  </span>
                )}
                <span className="text-gray-500">
                  ({stats.category_stats.dashboard.entries} total)
                </span>
              </div>
            </div>

            {/* Agentur-spezifischer Cache */}
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">Agenturen:</span>
              <div className="flex items-center gap-2">
                <span className="text-green-600 dark:text-green-400">
                  {stats.category_stats.agency_specific.fresh} aktuell
                </span>
                {stats.category_stats.agency_specific.stale > 0 && (
                  <span className="text-orange-600 dark:text-orange-400">
                    {stats.category_stats.agency_specific.stale} veraltet
                  </span>
                )}
                <span className="text-gray-500">
                  ({stats.category_stats.agency_specific.entries} total)
                </span>
              </div>
            </div>

            {/* Allgemeiner Cache */}
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">Allgemein:</span>
              <div className="flex items-center gap-2">
                <span className="text-green-600 dark:text-green-400">
                  {stats.category_stats.overall.fresh} aktuell
                </span>
                {stats.category_stats.overall.stale > 0 && (
                  <span className="text-orange-600 dark:text-orange-400">
                    {stats.category_stats.overall.stale} veraltet
                  </span>
                )}
                <span className="text-gray-500">
                  ({stats.category_stats.overall.entries} total)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detaillierte Freshness-Anzeige */}
      {showDetails && freshness && (
        <div className="border-t border-blue-200 dark:border-gray-600 pt-3">
          <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Datenaktualität Details</h4>
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