import React, { useState, useEffect } from 'react';

interface HeatmapData {
  agency_id: string;
  agency_name: string;
  event_type: string;
  count: number;
  percentage: number;
}

interface AgencyHeatmapProps {
  data: HeatmapData[];
  isLoading: boolean;
  onAgencyClick?: (agencyId: string, agencyName: string) => void;
}

const ProblematicStaysHeatmap: React.FC<AgencyHeatmapProps> = ({ 
  data, 
  isLoading,
  onAgencyClick 
}) => {
  const [processedData, setProcessedData] = useState<any[]>([]);
  const [eventTypes, setEventTypes] = useState<string[]>([]);
  
  // Process data for heatmap
  useEffect(() => {
    if (!data || data.length === 0) {
      setProcessedData([]);
      setEventTypes([]);
      return;
    }

    // Extract unique agencies and event types
    const agencies = Array.from(new Set(data.map(item => item.agency_name)));
    const uniqueEventTypes = Array.from(new Set(data.map(item => item.event_type)));
    
    // Create a more readable mapping for event types
    const eventTypeMapping: {[key: string]: string} = {
      'cancellation_before_arrival': 'Stornierung vor Anreise',
      'shortened_after_arrival': 'Vorzeitige Beendigung',
      'late_arrival': 'Verspätete Ankunft',
      'no_show': 'Nichterscheinen',
      'instant_departure': 'Sofortige Abreise',
      'customer_complaint': 'Kundenbeschwerde',
      'caretaker_complaint': 'Pflegekraftbeschwerde'
    };

    // Sort event types in a meaningful order
    const sortedEventTypes = uniqueEventTypes.sort((a, b) => {
      const orderA = Object.keys(eventTypeMapping).indexOf(a);
      const orderB = Object.keys(eventTypeMapping).indexOf(b);
      return orderA - orderB;
    });
    
    setEventTypes(sortedEventTypes);

    // Create data grid for each agency and event type
    const agencyData = agencies.map(agency => {
      const agencyItems = data.filter(item => item.agency_name === agency);
      
      // Find the agency ID from the filtered items
      const agencyId = agencyItems.length > 0 ? agencyItems[0].agency_id : '';
      
      // Create an object with all event types and their values
      const eventData: {[key: string]: number} = {};
      
      // Initialize with 0
      sortedEventTypes.forEach(type => {
        eventData[type] = 0;
      });
      
      // Fill in actual values
      agencyItems.forEach(item => {
        eventData[item.event_type] = item.percentage;
      });
      
      // Calculate total percentage across all event types for this agency
      const totalPercentage = Object.values(eventData).reduce((sum, value) => sum + value, 0);
      
      return {
        agency_id: agencyId,
        agency_name: agency,
        ...eventData,
        total: totalPercentage
      };
    });
    
    // Sort by total percentage (highest first)
    const sortedData = agencyData.sort((a, b) => b.total - a.total);
    
    setProcessedData(sortedData);
  }, [data]);

  // Function to get color intensity based on value
  const getColorIntensity = (value: number): string => {
    // Max percentage is likely around 5-10%, adjust as needed
    const normalizedValue = Math.min(value / 10, 1);
    
    // Red color with varying opacity
    return `rgba(239, 68, 68, ${normalizedValue.toFixed(2)})`;
  };

  // Format percentage
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm animate-pulse h-96">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
        <div className="h-full bg-gray-100 dark:bg-gray-700 rounded"></div>
      </div>
    );
  }

  if (!data || data.length === 0 || !processedData || processedData.length === 0) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm">
        <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Problemverteilung nach Agentur</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Keine Daten verfügbar</p>
      </div>
    );
  }

  // Get user-friendly event type names
  const getEventTypeName = (type: string): string => {
    const mapping: {[key: string]: string} = {
      'cancellation_before_arrival': 'Stornierung vor Anreise',
      'shortened_after_arrival': 'Vorzeitige Beendigung',
      'late_arrival': 'Verspätete Ankunft',
      'no_show': 'Nichterscheinen',
      'instant_departure': 'Sofortige Abreise',
      'customer_complaint': 'Kundenbeschwerde',
      'caretaker_complaint': 'Pflegekraftbeschwerde'
    };
    return mapping[type] || type;
  };

  return (
    <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm">
      <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Problemverteilung nach Agentur</h3>
      
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-700">
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider sticky left-0 bg-gray-50 dark:bg-gray-700 z-10">
                Agentur
              </th>
              {eventTypes.map(type => (
                <th key={type} className="px-3 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {getEventTypeName(type)}
                </th>
              ))}
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Gesamt
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {processedData.map((agency, index) => (
              <tr 
                key={agency.agency_id} 
                className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700/50' : 'bg-white dark:bg-gray-800'}
                onClick={() => onAgencyClick && onAgencyClick(agency.agency_id, agency.agency_name)}
              >
                <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 sticky left-0 bg-inherit z-10 cursor-pointer">
                  {agency.agency_name}
                </td>
                {eventTypes.map(type => (
                  <td 
                    key={`${agency.agency_id}-${type}`} 
                    className="px-3 py-2 whitespace-nowrap text-sm text-center cursor-pointer"
                    style={{ 
                      backgroundColor: getColorIntensity(agency[type]),
                      color: agency[type] > 5 ? 'white' : 'black' 
                    }}
                  >
                    {formatPercentage(agency[type])}
                  </td>
                ))}
                <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 text-center cursor-pointer">
                  {formatPercentage(agency.total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 flex justify-between items-center">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Klicken Sie auf eine Agentur für detaillierte Informationen
        </div>
        <div className="flex items-center">
          <div className="w-24 h-4 bg-gradient-to-r from-white dark:from-gray-800 to-red-500"></div>
          <div className="text-xs text-gray-500 dark:text-gray-400 ml-2">
            0% bis &gt;10%
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProblematicStaysHeatmap;