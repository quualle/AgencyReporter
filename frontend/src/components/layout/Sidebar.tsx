import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAppStore } from '../../store/appStore';
import TimeFilter from '../common/TimeFilter';
import { preloadService } from '../../services/api';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { 
    activeTab, 
    setActiveTab, 
    selectedAgency, 
    setPreloadStatus, 
    setShowPreloadOverlay,
    preloadStatus
  } = useAppStore();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  const handlePreloadClick = async () => {
    if (!selectedAgency) return;
    
    // Zeige das Overlay an
    setShowPreloadOverlay(true);
    
    // Initialisiere den Preload-Status
    setPreloadStatus({
      totalRequests: 1,
      completedRequests: 0,
      inProgress: true,
      status: 'Initialisiere Datenladung...'
    });
    
    // Starte den Preload-Prozess
    await preloadService.preloadAllData(
      selectedAgency.agency_id,
      (progress) => {
        // Aktualisiere den Status im Store
        setPreloadStatus(progress);
      }
    );
  };

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 shadow-sm hidden md:block">
      <div className="p-4">
        <h2 className="text-xl font-semibold mb-6 text-gray-800 dark:text-white">Navigation</h2>
        
        <nav>
          <ul className="space-y-2">
            <li>
              <Link 
                to="/"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                </svg>
                Dashboard
                <sup className="text-[8px] font-normal text-yellow-600 ml-0.5">In Entwicklung</sup>
              </Link>
            </li>
            <li>
              <Link 
                to="/quotas"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/quotas') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                </svg>
                Quoten
              </Link>
            </li>
            <li>
              <Link 
                to="/response-times"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/response-times') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                Reaktionszeiten
              </Link>
            </li>
            <li>
              <Link 
                to="/problematic-stays"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/problematic-stays') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Problemeinsätze
              </Link>
            </li>
            <li>
              <Link 
                to="/quality"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/quality') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Qualität
                <sup className="text-[8px] font-normal text-yellow-600 ml-0.5">In Entwicklung</sup>
              </Link>
            </li>
            <li>
              <Link 
                to="/strength-weakness"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/strength-weakness') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                </svg>
                <span>Stärken/Schwächen</span>
                <sup className="text-[8px] font-normal text-yellow-600 ml-0.5">In Entwicklung</sup>
              </Link>
            </li>
            <li>
              <Link 
                to="/llm-analysis"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/llm-analysis') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
                KI-Analyse
                <sup className="text-[8px] font-normal text-yellow-600 ml-0.5">In Entwicklung</sup>
              </Link>
            </li>
            <li>
              <Link 
                to="/agency-comparison"
                className={`flex items-center px-4 py-2 rounded-md ${
                  isActive('/agency-comparison') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-300' 
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                Agenturvergleich
              </Link>
            </li>
          </ul>
        </nav>
        
        <div className="mt-8">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Zeitraum</h3>
          <TimeFilter />
        </div>
        
        <div className="mt-8">
          <button
            onClick={handlePreloadClick}
            disabled={!selectedAgency || (preloadStatus?.inProgress || false)}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-md 
              ${!selectedAgency || (preloadStatus?.inProgress || false)
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400'
                : 'bg-primary-600 text-white hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-800'
              } transition-colors duration-200 ease-in-out`}
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            {preloadStatus?.inProgress 
              ? `Lädt... (${preloadStatus.completedRequests}/${preloadStatus.totalRequests})` 
              : 'Alle Daten laden'}
          </button>
          {preloadStatus && !preloadStatus.inProgress && !preloadStatus.error && (
            <p className="text-xs text-green-600 mt-2 text-center">
              Daten erfolgreich geladen!
            </p>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar; 