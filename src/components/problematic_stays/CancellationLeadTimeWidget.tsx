import React from 'react';

interface CancellationLeadTimeWidgetProps {
  data: any[];
  isLoading: boolean;
}

const CancellationLeadTimeWidget: React.FC<CancellationLeadTimeWidgetProps> = ({ data, isLoading }) => {
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Abbrüche - Vorlaufzeit zum geplanten Einsatzbeginn
        </h3>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Temporäre Test-Version
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <p className="text-gray-600 dark:text-gray-300">
          API-Endpunkt noch nicht verfügbar. Die vollständige Version wird bald angezeigt.
        </p>
      </div>
    </div>
  );
};

export default CancellationLeadTimeWidget; 