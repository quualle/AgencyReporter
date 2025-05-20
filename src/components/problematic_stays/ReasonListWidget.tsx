import React, { useState } from 'react';

interface ReasonListWidgetProps {
  reasonsData: any[];
  isLoading: boolean;
  eventType: 'shortened_after_arrival' | 'cancelled_before_arrival';
}

const ReasonListWidget: React.FC<ReasonListWidgetProps> = ({ reasonsData, isLoading, eventType }) => {
  const [stayType, setStayType] = useState<'all' | 'first_stay' | 'follow_stay'>('all');

  if (isLoading) {
    return <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />;
  }

  // Filtere und sortiere die Gründe nach stayType und eventType
  const filteredReasons = (reasonsData || [])
    .filter((item: any) => {
      if (item.event_type !== eventType) return false;
      if (stayType === 'all') return true;
      return item.stay_type === stayType;
    })
    .sort((a: any, b: any) => b.count - a.count);

  // Berechne die Gesamtanzahl für Prozentangaben
  const total = filteredReasons.reduce((sum: number, item: any) => sum + (item.count || 0), 0);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          {eventType === 'cancelled_before_arrival' ? 'Gründe für Abbruch' : 'Gründe für vorzeitige Beendigungen'}
        </h3>
        <div className="flex space-x-2">
          <button
            className={`px-2 py-1 text-sm rounded-md ${stayType === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
            onClick={() => setStayType('all')}
          >
            Alle
          </button>
          <button
            className={`px-2 py-1 text-sm rounded-md ${stayType === 'first_stay' ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
            onClick={() => setStayType('first_stay')}
          >
            Ersteinsätze
          </button>
          <button
            className={`px-2 py-1 text-sm rounded-md ${stayType === 'follow_stay' ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
            onClick={() => setStayType('follow_stay')}
          >
            Wechseleinsätze
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-700">
          <thead>
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Grund</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Anzahl</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Anteil</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
            {filteredReasons.length === 0 && (
              <tr>
                <td colSpan={3} className="px-3 py-2 text-center text-gray-500 dark:text-gray-400">Keine Gründe vorhanden.</td>
              </tr>
            )}
            {filteredReasons.map((item: any, idx: number) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : 'bg-white dark:bg-gray-800'}>
                <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{item.reason || 'Unbekannt'}</td>
                <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{item.count}</td>
                <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{total > 0 ? ((item.count / total) * 100).toFixed(1) + '%' : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReasonListWidget; 