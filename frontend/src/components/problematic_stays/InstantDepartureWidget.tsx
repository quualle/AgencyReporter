import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, TooltipProps 
} from 'recharts';

interface InstantDepartureWidgetProps {
  data: any[];
  isLoading: boolean;
}

const InstantDepartureWidget: React.FC<InstantDepartureWidgetProps> = ({ data, isLoading }) => {
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Daten für sofortige Abreisen extrahieren
  const stats = data[0];
  const instantDepartureData = [];

  // Erstelle ein Array mit den Daten für jede Anzahl an Tagen (1-9)
  for (let i = 1; i <= 9; i++) {
    const key = `instant_departure_day_${i}`;
    instantDepartureData.push({
      name: `${i} ${i === 1 ? 'Tag' : 'Tage'}`,
      value: stats[key] || 0,
    });
  }

  // Berechne den Gesamtwert für die Prozentangabe
  const totalInstantDepartures = instantDepartureData.reduce((sum, entry) => sum + entry.value, 0);
  
  // Farben je nach Kritikalität (rot für frühere Abreisen, orange für spätere)
  const getBarColor = (index: number) => {
    const colors = [
      '#ef4444', // Tag 1 (rot)
      '#f97316', // Tag 2 (orange-rot)
      '#f59e0b', // Tag 3
      '#eab308', // Tag 4
      '#84cc16', // Tag 5
      '#22c55e', // Tag 6
      '#10b981', // Tag 7
      '#06b6d4', // Tag 8
      '#0ea5e9'  // Tag 9 (blau)
    ];
    return colors[index];
  };

  // Benutzerdefinierte Tooltip-Komponente
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const value = payload[0].value as number;
      const percentage = totalInstantDepartures > 0 ? (value / totalInstantDepartures * 100).toFixed(1) : '0';
      
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
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Sofortige Abreisen (&lt;10 Tage)
        </h3>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Gesamt: {totalInstantDepartures}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={instantDepartureData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              barSize={30}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="value" name="Anzahl Abreisen">
                {instantDepartureData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(index)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
          <p>
            {totalInstantDepartures > 0 
              ? `${(instantDepartureData[0].value / totalInstantDepartures * 100).toFixed(1)}% aller sofortigen Abreisen erfolgen bereits am ersten Tag.`
              : 'Keine sofortigen Abreisen im ausgewählten Zeitraum.'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default InstantDepartureWidget; 