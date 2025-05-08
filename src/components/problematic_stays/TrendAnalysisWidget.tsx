import React, { useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, TooltipProps, Area, AreaChart
} from 'recharts';

interface TrendAnalysisWidgetProps {
  data: any[];
  isLoading: boolean;
}

const TrendAnalysisWidget: React.FC<TrendAnalysisWidgetProps> = ({ data, isLoading }) => {
  const [dataType, setDataType] = useState<string>('count');
  
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-80 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Gruppieren der Daten nach Monat
  const prepareMonthlyData = () => {
    // Sortiere Daten nach Datum
    const sortedData = [...data].sort((a, b) => {
      return new Date(a.event_month + '-01').getTime() - new Date(b.event_month + '-01').getTime();
    });
    
    // Gruppiere nach Monat und Event-Typ
    const monthlyDataMap = new Map();
    
    sortedData.forEach(item => {
      const month = item.event_month;
      if (!monthlyDataMap.has(month)) {
        monthlyDataMap.set(month, {
          month: month,
          date: new Date(month + '-01'),
          total: 0,
          cancelled_before_arrival: 0,
          shortened_after_arrival: 0,
          satisfied_count: 0,
          not_satisfied_count: 0,
          instant_departure_count: 0,
          with_replacement_count: 0,
          with_follow_up_count: 0,
          avg_reason_confidence: 0,
          entries: 0
        });
      }
      
      const monthData = monthlyDataMap.get(month);
      monthData.total += item.count;
      monthData.entries += 1;
      
      if (item.event_type === 'cancelled_before_arrival') {
        monthData.cancelled_before_arrival += item.count;
      } else if (item.event_type === 'shortened_after_arrival') {
        monthData.shortened_after_arrival += item.count;
      }
      
      monthData.satisfied_count += item.satisfied_count || 0;
      monthData.not_satisfied_count += item.not_satisfied_count || 0;
      monthData.instant_departure_count += item.instant_departure_count || 0;
      monthData.with_replacement_count += item.with_replacement_count || 0;
      monthData.with_follow_up_count += item.with_follow_up_count || 0;
      
      // Gewichteter Durchschnitt für Konfidenz
      monthData.avg_reason_confidence += (item.avg_reason_confidence || 0) * item.count;
    });
    
    // Berechne durchschnittliche Konfidenz
    monthlyDataMap.forEach(item => {
      if (item.total > 0) {
        item.avg_reason_confidence = Math.round(item.avg_reason_confidence / item.total);
      }
    });
    
    // Umwandeln in ein Array und sortieren
    return Array.from(monthlyDataMap.values())
      .sort((a, b) => a.date.getTime() - b.date.getTime());
  };

  const monthlyData = prepareMonthlyData();
  
  // Formatiere Monat für die Anzeige
  const formatMonth = (month: string) => {
    const [year, monthNum] = month.split('-');
    const date = new Date(parseInt(year), parseInt(monthNum) - 1, 1);
    return date.toLocaleDateString('de-DE', { month: 'short', year: '2-digit' });
  };

  // Angepasste Tooltip-Komponente
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white">
            {formatMonth(data.month)}
          </p>
          <div className="mt-2 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Gesamt: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {data.total}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Vor Anreise: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {data.cancelled_before_arrival}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Nach Anreise: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {data.shortened_after_arrival}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Zufriedene Kunden: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {data.satisfied_count}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Unzufriedene Kunden: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {data.not_satisfied_count}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Problematische Einsätze - Zeitliche Entwicklung
        </h3>
        <div>
          <select
            value={dataType}
            onChange={(e) => setDataType(e.target.value)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            <option value="count">Anzahl</option>
            <option value="satisfaction">Kundenzufriedenheit</option>
            <option value="ersatz">Ersatz & Folgeeinsätze</option>
          </select>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            {dataType === 'count' ? (
              <AreaChart
                data={monthlyData}
                margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month" 
                  tickFormatter={formatMonth} 
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="cancelled_before_arrival" 
                  name="Vor Anreise" 
                  stackId="1"
                  stroke="#ef4444" 
                  fill="#fecaca"
                />
                <Area 
                  type="monotone" 
                  dataKey="shortened_after_arrival" 
                  name="Nach Anreise" 
                  stackId="1"
                  stroke="#f59e0b" 
                  fill="#fde68a"
                />
              </AreaChart>
            ) : dataType === 'satisfaction' ? (
              <LineChart
                data={monthlyData}
                margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month" 
                  tickFormatter={formatMonth} 
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="satisfied_count" 
                  name="Zufriedene Kunden" 
                  stroke="#22c55e" 
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="not_satisfied_count" 
                  name="Unzufriedene Kunden" 
                  stroke="#ef4444" 
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="avg_reason_confidence" 
                  name="KI-Konfidenz (%)" 
                  stroke="#6366f1" 
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            ) : (
              <LineChart
                data={monthlyData}
                margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month" 
                  tickFormatter={formatMonth} 
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="with_replacement_count" 
                  name="Mit Ersatz" 
                  stroke="#0ea5e9" 
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="with_follow_up_count" 
                  name="Mit Folgeeinsatz" 
                  stroke="#8b5cf6" 
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="instant_departure_count" 
                  name="Sofortige Abreisen" 
                  stroke="#f43f5e" 
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
        <div className="text-center mt-3 text-sm text-gray-600 dark:text-gray-400">
          {dataType === 'count' ? (
            <p>Entwicklung der problematischen Einsätze über Zeit</p>
          ) : dataType === 'satisfaction' ? (
            <p>Entwicklung der Kundenzufriedenheit und KI-Konfidenz</p>
          ) : (
            <p>Entwicklung der Ersatzstellungen und Folgeeinsätze</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrendAnalysisWidget; 