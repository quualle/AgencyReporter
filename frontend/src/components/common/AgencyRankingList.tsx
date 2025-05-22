import React from 'react';

export interface AgencyData {
  agency_id: string;
  agency_name: string;
  value: number;
  total_count?: number;
}

interface AgencyRankingListProps {
  title: string;
  agencies: AgencyData[];
  metric: string;
  formatValue: (value: number) => string;
  showTotal?: boolean;
  isLoading?: boolean;
  limit?: number;
  type?: 'top' | 'bottom';
  onAgencyClick?: (agencyId: string, agencyName: string) => void;
  valueLabel?: string;
  totalLabel?: string;
}

const AgencyRankingList: React.FC<AgencyRankingListProps> = ({
  title,
  agencies,
  metric,
  formatValue,
  showTotal = false,
  isLoading = false,
  limit = 5,
  type = 'top',
  onAgencyClick,
  valueLabel = 'Wert',
  totalLabel = 'Gesamt'
}) => {
  // Sort agencies based on type
  const sortedAgencies = [...agencies].sort((a, b) => {
    return type === 'top'
      ? b.value - a.value // Top: highest first
      : a.value - b.value; // Bottom: lowest first
  }).slice(0, limit);

  if (isLoading) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm animate-pulse">
        <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
        {Array.from({ length: limit }).map((_, index) => (
          <div key={index} className="h-10 bg-gray-100 dark:bg-gray-700 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  if (!agencies || agencies.length === 0) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm">
        <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">{title}</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Keine Daten verfügbar</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm h-full flex flex-col">
      <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">{title}</h3>
      
      <div className="text-xs text-gray-500 dark:text-gray-400 grid grid-cols-12 mb-2 px-2 bg-white dark:bg-gray-800 sticky top-0 z-10 py-1">
        <div className="col-span-1">#</div>
        <div className="col-span-7">Agentur</div>
        <div className="col-span-2 text-right">{valueLabel}</div>
        {showTotal && <div className="col-span-2 text-right">{totalLabel}</div>}
      </div>
      
      <div className="space-y-2 overflow-y-auto pr-1 max-h-96 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent">
        {sortedAgencies.map((agency, index) => (
          <div 
            key={agency.agency_id}
            className={`rounded-md p-2 grid grid-cols-12 items-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 ${
              type === 'top' 
                ? index === 0 
                  ? 'bg-green-50 dark:bg-green-900/20' 
                  : index === 1 
                    ? 'bg-green-50/70 dark:bg-green-900/10' 
                    : ''
                : index === 0 
                  ? 'bg-red-50 dark:bg-red-900/20' 
                  : index === 1 
                    ? 'bg-red-50/70 dark:bg-red-900/10' 
                    : ''
            }`}
            onClick={() => onAgencyClick && onAgencyClick(agency.agency_id, agency.agency_name)}
          >
            <div className="col-span-1 font-medium text-gray-600 dark:text-gray-300">
              {index + 1}
            </div>
            <div className="col-span-7 font-medium text-gray-800 dark:text-gray-200 truncate" title={agency.agency_name}>
              {agency.agency_name}
            </div>
            <div className="col-span-2 font-semibold text-right">
              <span className={`
                ${type === 'top' 
                  ? index < 3 ? 'text-green-600 dark:text-green-400' : 'text-gray-700 dark:text-gray-300' 
                  : index < 3 ? 'text-red-600 dark:text-red-400' : 'text-gray-700 dark:text-gray-300'}
              `}>
                {formatValue(agency.value)}
              </span>
            </div>
            {showTotal && (
              <div className="col-span-2 text-gray-500 dark:text-gray-400 text-right">
                {agency.total_count !== undefined ? agency.total_count.toLocaleString() : '-'}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgencyRankingList;