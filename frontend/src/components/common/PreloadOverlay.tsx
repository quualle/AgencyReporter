import React from 'react';
import { useAppStore } from '../../store/appStore';
import { PreloadProgress } from '../../services/api';

const PreloadOverlay: React.FC = () => {
  const { 
    preloadStatus, 
    showPreloadOverlay, 
    setShowPreloadOverlay 
  } = useAppStore();

  // Wenn der Overlay nicht angezeigt werden soll oder kein Status existiert
  if (!showPreloadOverlay || !preloadStatus) {
    return null;
  }

  // Berechne Fortschritt in Prozent
  const progress = preloadStatus.completedRequests / Math.max(preloadStatus.totalRequests, 1) * 100;
  
  // Wenn der Ladevorgang abgeschlossen ist und kein Fehler aufgetreten ist,
  // schließe den Overlay nach 2 Sekunden
  if (!preloadStatus.inProgress && !preloadStatus.error) {
    setTimeout(() => {
      setShowPreloadOverlay(false);
    }, 2000);
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full">
        <div className="flex flex-col items-center">
          {/* Überschrift */}
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
            Daten werden geladen
          </h2>

          {/* Statusmeldung */}
          <p className="text-gray-600 dark:text-gray-300 mb-4 text-center">
            {preloadStatus.status}
          </p>

          {/* Fortschrittsbalken */}
          <div className="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-2">
            <div 
              className={`h-full rounded-full transition-all duration-300 ease-out ${
                preloadStatus.error ? 'bg-red-500' : 'bg-primary-500'
              }`}
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          {/* Numerischer Fortschritt */}
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            {preloadStatus.completedRequests} von {preloadStatus.totalRequests} Abfragen abgeschlossen
            ({Math.round(progress)}%)
          </p>

          {/* Bei Fehler einen Fehlermeldung anzeigen */}
          {preloadStatus.error && (
            <div className="text-red-500 mb-4 text-center">
              <p className="font-semibold">Ein Fehler ist aufgetreten:</p>
              <p>{preloadStatus.error}</p>
            </div>
          )}

          {/* Wenn der Ladevorgang abgeschlossen ist, zeige eine Erfolgsmeldung an */}
          {!preloadStatus.inProgress && !preloadStatus.error && (
            <div className="text-green-500 mb-4 text-center">
              <p className="font-semibold">Alle Daten erfolgreich geladen!</p>
              <p>Die Anwendung sollte nun deutlich schneller reagieren.</p>
            </div>
          )}

          {/* Schließen-Button (nur anzeigen, wenn Ladevorgang abgeschlossen oder Fehler aufgetreten ist) */}
          {(!preloadStatus.inProgress || preloadStatus.error) && (
            <button
              onClick={() => setShowPreloadOverlay(false)}
              className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
            >
              Schließen
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PreloadOverlay;