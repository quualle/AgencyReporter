import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  Cell, TooltipProps 
} from 'recharts';

interface DistributionWidgetProps {
  data: any[];
  isLoading: boolean;
}

const DistributionWidget: React.FC<DistributionWidgetProps> = ({ data, isLoading }) => {
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Extrahiere relevante Daten für das Diagramm
  const chartData = [
    {
      name: 'Abbrüche vor Anreise',
      'Ersteinsatz': data[0]?.first_stay_cancelled_count || 0,
      'Wechseleinsatz': data[0]?.follow_stay_cancelled_count || 0,
    },
    {
      name: 'Vorzeitige Beendigungen',
      'Ersteinsatz': data[0]?.first_stay_shortened_count || 0,
      'Wechseleinsatz': data[0]?.follow_stay_shortened_count || 0,
    },
  ];

  // Benutzerdefinierte Tooltip-Komponente
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum, entry) => sum + (entry.value as number), 0);
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white">{label}</p>
          <div className="mt-2">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 mr-2" 
                    style={{ backgroundColor: entry.color }}
                  ></div>
                  <span className="text-gray-700 dark:text-gray-300">{entry.name}: </span>
                </div>
                <span className="font-medium ml-2 text-gray-900 dark:text-white">
                  {entry.value} ({((entry.value as number) / total * 100).toFixed(1)}%)
                </span>
              </div>
            ))}
            <div className="mt-1 pt-1 border-t border-gray-200 dark:border-gray-700">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">Gesamt:</span>
                <span className="font-medium text-gray-900 dark:text-white">{total}</span>
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey="Ersteinsatz" 
            stackId="a" 
            fill="#4f46e5" 
            name="Ersteinsatz" 
          />
          <Bar 
            dataKey="Wechseleinsatz" 
            stackId="a" 
            fill="#10b981" 
            name="Wechseleinsatz" 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DistributionWidget; 