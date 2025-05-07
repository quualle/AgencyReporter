import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';

interface FollowUpAnalysisWidgetProps {
  data: any[];
  isLoading: boolean;
}

const FollowUpAnalysisWidget: React.FC<FollowUpAnalysisWidgetProps> = ({ data, isLoading }) => {
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-80 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Daten für das Donut-Chart vorbereiten
  const prepareChartData = () => {
    // Nutze das erste Element, da wir eine Zusammenfassung erwarten
    const overview = data[0] || {};
    
    // Extrahiere die relevanten Werte
    const withFollowUp = overview.with_follow_up_count || 0;
    const withoutFollowUp = overview.without_follow_up_count || 0;

    return [
      { name: 'Mit Folgeeinsatz', value: withFollowUp, color: '#22c55e' }, // Grün
      { name: 'Ohne Folgeeinsatz', value: withoutFollowUp, color: '#ef4444' } // Rot
    ].filter(item => item.value > 0); // Nur Elemente mit Werten > 0 anzeigen
  };

  const chartData = prepareChartData();
  
  // Berechne den Gesamtwert für Prozentangaben
  const totalItems = chartData.reduce((sum, item) => sum + item.value, 0);
  
  // Berechne die Folgeeinsatzquote
  const followUpRate = totalItems > 0 
    ? (chartData.find(item => item.name === 'Mit Folgeeinsatz')?.value || 0) / totalItems * 100 
    : 0;

  // Extrahiere den Vergleichswert (Durchschnitt über alle Agenturen)
  const averageRate = data[0]?.average_follow_up_rate || 0;
  
  // Berechne die Differenz zum Durchschnitt
  const difference = followUpRate - averageRate;

  // Benutzerdefinierter Tooltip für das Donut-Chart
  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      const percentage = totalItems > 0 ? (item.value / totalItems * 100).toFixed(1) : '0';
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white">{item.name}</p>
          <div className="mt-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Anzahl: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {item.value}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Anteil: </span>
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

  // Trend-Indikator basierend auf der Differenz zum Durchschnitt
  const TrendIndicator = () => {
    // Positiv: Mehr Folgeeinsätze als Durchschnitt
    if (difference > 0) {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
      );
    } 
    // Negativ: Weniger Folgeeinsätze als Durchschnitt
    else if (difference < 0) {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-red-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      );
    } 
    // Neutral: Gleich wie Durchschnitt
    else {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M4 9h12a1 1 0 010 2H4a1 1 0 110-2zm0-4h12a1 1 0 110 2H4a1 1 0 010-2z" clipRule="evenodd" />
        </svg>
      );
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 h-full">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">
        Folgeeinsatzanalyse
      </h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Donut-Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#8884d8'} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* KPI-Statistiken */}
        <div className="flex flex-col justify-center">
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Folgeeinsatzquote</h4>
            <div className="mt-1">
              <span className="text-3xl font-bold text-gray-900 dark:text-white">
                {followUpRate.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center mt-1 text-sm">
              <span className="text-gray-500 dark:text-gray-400">vs. Durchschnitt: </span>
              <span className={`font-medium ml-1 ${difference > 0 ? 'text-green-500' : difference < 0 ? 'text-red-500' : 'text-gray-500'}`}>
                {Math.abs(difference).toFixed(1)}%
              </span>
              <TrendIndicator />
            </div>
          </div>
          
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Einsätze mit Folgeeinsatz</h4>
            <div className="mt-1">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {chartData.find(item => item.name === 'Mit Folgeeinsatz')?.value || 0}
              </span>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">Einsätze ohne Folgeeinsatz</h4>
            <div className="mt-1">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {chartData.find(item => item.name === 'Ohne Folgeeinsatz')?.value || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>
          {followUpRate > averageRate 
            ? 'Überdurchschnittlich hohe Folgeeinsatzquote bei verkürzten Einsätzen.'
            : followUpRate < averageRate 
            ? 'Unterdurchschnittlich niedrige Folgeeinsatzquote bei verkürzten Einsätzen.'
            : 'Folgeeinsatzquote entspricht dem Durchschnitt.'}
        </p>
      </div>
    </div>
  );
};

export default FollowUpAnalysisWidget; 