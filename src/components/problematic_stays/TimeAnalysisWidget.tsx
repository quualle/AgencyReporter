import React, { useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ReferenceLine, TooltipProps
} from 'recharts';

interface TimeAnalysisWidgetProps {
  data: any[];
  isLoading: boolean;
  eventType: 'cancelled_before_arrival' | 'shortened_after_arrival';
  title: string;
}

const TimeAnalysisWidget: React.FC<TimeAnalysisWidgetProps> = ({ 
  data, 
  isLoading,
  eventType,
  title
}) => {
  const [stayType, setStayType] = useState<string>('all'); // 'all', 'first_stay', 'follow_stay'

  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Filtern und Aufbereiten der Daten für die Darstellung
  let chartData: any[] = [];
  let averageValue = 0;

  // Berechne den Durchschnittswert für die Referenzlinie
  if (eventType === 'cancelled_before_arrival') {
    // Daten für Abbrüche vor Anreise - zeigt Tage vor Anreise
    if (stayType === 'all' || stayType === 'first_stay') {
      averageValue += (data[0]?.first_stay_avg_days_before_arrival || 0);
    }
    
    if (stayType === 'all' || stayType === 'follow_stay') {
      averageValue += (data[0]?.follow_stay_avg_days_before_arrival || 0);
    }

    if (stayType === 'all') {
      averageValue /= 2; // Durchschnitt bei beiden Einsatztypen
    }

    // Gruppiere die Daten in Tagesbereiche für Abbrüche vor Anreise
    const cancelledGroupedData = [
      { name: '1-3 Tage', value: data[0]?.cancelled_1_3_days || 0 },
      { name: '4-7 Tage', value: data[0]?.cancelled_4_7_days || 0 },
      { name: '8-14 Tage', value: data[0]?.cancelled_8_14_days || 0 },
      { name: '15-30 Tage', value: data[0]?.cancelled_15_30_days || 0 },
      { name: '>30 Tage', value: data[0]?.cancelled_over_30_days || 0 }
    ];

    chartData = cancelledGroupedData;
  } else {
    // Daten für vorzeitige Beendigungen - zeigt Tage der Verkürzung
    if (stayType === 'all' || stayType === 'first_stay') {
      averageValue += (data[0]?.first_stay_avg_shortened_days || 0);
    }
    
    if (stayType === 'all' || stayType === 'follow_stay') {
      averageValue += (data[0]?.follow_stay_avg_shortened_days || 0);
    }

    if (stayType === 'all') {
      averageValue /= 2; // Durchschnitt bei beiden Einsatztypen
    }

    // Gruppiere die Daten in Tagesbereiche für vorzeitige Beendigungen
    const shortenedGroupedData = [
      { name: '14-21 Tage', value: data[0]?.shortened_14_21_days || 0 },
      { name: '22-30 Tage', value: data[0]?.shortened_22_30_days || 0 },
      { name: '31-60 Tage', value: data[0]?.shortened_31_60_days || 0 },
      { name: '61-90 Tage', value: data[0]?.shortened_61_90_days || 0 },
      { name: '>90 Tage', value: data[0]?.shortened_over_90_days || 0 }
    ];

    chartData = shortenedGroupedData;
  }

  // Benutzerdefinierte Tooltip-Komponente
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const value = payload[0].value as number;
      const total = chartData.reduce((sum, entry) => sum + entry.value, 0);
      const percentage = total > 0 ? (value / total * 100).toFixed(1) : '0';
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white">{label}</p>
          <div className="mt-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Anzahl: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {value}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Prozent: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {percentage}%
              </span>
            </div>
          </div>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">{title}</h3>
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

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              barSize={40}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <ReferenceLine
                y={averageValue}
                label={{
                  value: `Ø ${averageValue.toFixed(1)} Tage`,
                  position: 'top',
                  fill: '#666',
                  fontSize: 12
                }}
                stroke="#666"
                strokeDasharray="3 3"
              />
              <Bar
                dataKey="value"
                name={eventType === 'cancelled_before_arrival' ? 'Abbrüche nach Vorlaufzeit' : 'Verkürzungen nach Tagen'}
                fill={eventType === 'cancelled_before_arrival' ? '#4f46e5' : '#ef4444'}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
          <p>
            {eventType === 'cancelled_before_arrival' 
              ? `Durchschnittliche Vorlaufzeit vor Anreise: ${averageValue.toFixed(1)} Tage`
              : `Durchschnittliche Verkürzungsdauer: ${averageValue.toFixed(1)} Tage`
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default TimeAnalysisWidget; 