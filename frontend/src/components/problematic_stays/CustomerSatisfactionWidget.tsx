import React, { useState } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, 
  TooltipProps, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend
} from 'recharts';

interface CustomerSatisfactionWidgetProps {
  data: any[];
  isLoading: boolean;
}

// Typen für die Satisfactions
type SatisfactionKey = 'satisfied' | 'not_satisfied' | 'neutral' | 'zufrieden' | 'n/a';

interface SatisfactionCount {
  satisfied: number;
  not_satisfied: number;
  neutral: number;
}

interface SatisfactionDataItem {
  name: string;
  value: number;
  key: SatisfactionKey;
}

const CustomerSatisfactionWidget: React.FC<CustomerSatisfactionWidgetProps> = ({ data, isLoading }) => {
  const [selectedSatisfaction, setSelectedSatisfaction] = useState<SatisfactionKey | null>(null);
  
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-80 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Farben für die verschiedenen Zufriedenheitsgrade
  const satisfactionColors: Record<SatisfactionKey, string> = {
    satisfied: '#22c55e',   // Grün
    not_satisfied: '#ef4444',  // Rot
    neutral: '#f59e0b',  // Orange
    zufrieden: '#22c55e',   // Deutsch equivalent
    'n/a': '#94a3b8'  // Grau für N/A
  };

  // Daten für die Zufriedenheitsverteilung aufbereiten
  const prepareSatisfactionData = (): SatisfactionDataItem[] => {
    const satisfactionCount: SatisfactionCount = {
      satisfied: 0,
      not_satisfied: 0,
      neutral: 0
    };
    
    // Zähle die verschiedenen Zufriedenheitsgrade
    data.forEach(item => {
      // Mapping deutscher Begriffe auf englische Keys
      let satisfaction: SatisfactionKey;
      if (item.satisfaction === 'zufrieden') {
        satisfaction = 'satisfied';
      } else if (item.satisfaction === 'n/a') {
        satisfaction = 'neutral';
      } else if (item.satisfaction === 'satisfied' || item.satisfaction === 'not_satisfied') {
        satisfaction = item.satisfaction as SatisfactionKey;
      } else {
        satisfaction = 'neutral';
      }
      
      if (satisfaction in satisfactionCount) {
        satisfactionCount[satisfaction as keyof SatisfactionCount] += item.count;
      } else {
        satisfactionCount.neutral += item.count;
      }
    });
    
    // In ein Format für das Pie-Chart umwandeln
    const chartData: SatisfactionDataItem[] = [
      { name: 'Zufrieden', value: satisfactionCount.satisfied, key: 'satisfied' },
      { name: 'Unzufrieden', value: satisfactionCount.not_satisfied, key: 'not_satisfied' },
      { name: 'Neutral/Unbekannt', value: satisfactionCount.neutral, key: 'neutral' }
    ];
    
    return chartData.filter(item => item.value > 0);
  };
  
  // Daten für die Visualisierung der Zufriedenheit nach Gründen
  const prepareReasonsBySatisfactionData = () => {
    // Nur Einträge mit der ausgewählten Zufriedenheit filtern
    const filteredData = selectedSatisfaction 
      ? data.filter(item => 
          item.satisfaction === selectedSatisfaction || 
          (selectedSatisfaction === 'satisfied' && item.satisfaction === 'zufrieden'))
      : data;
      
    // Gruppiere nach Gründen
    const reasonsMap = new Map();
    filteredData.forEach(item => {
      const reason = item.reason || 'Unbekannt';
      if (!reasonsMap.has(reason)) {
        reasonsMap.set(reason, {
          name: reason,
          count: 0,
          satisfaction: item.satisfaction,
          avg_confidence: 0,
          confidenceSum: 0,
          entries: 0
        });
      }
      
      const reasonData = reasonsMap.get(reason);
      reasonData.count += item.count;
      reasonData.confidenceSum += (item.avg_confidence * item.count);
      reasonData.entries += item.count;
    });
    
    // Berechne Durchschnitts-Konfidenz und formatiere Daten
    return Array.from(reasonsMap.values())
      .map(item => ({
        name: item.name.length > 30 ? item.name.substring(0, 28) + '...' : item.name,
        fullName: item.name,
        count: item.count,
        satisfaction: item.satisfaction,
        avg_confidence: item.entries > 0 ? Math.round(item.confidenceSum / item.entries) : 0
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10); // Top 10 Gründe
  };

  const satisfactionData = prepareSatisfactionData();
  const reasonsBySatisfactionData = prepareReasonsBySatisfactionData();
  
  // Berechne den Gesamtwert für die Prozentangabe
  const totalItems = satisfactionData.reduce((sum, item) => sum + item.value, 0);
  
  // Benutzerdefinierte Tooltip-Komponente für Pie-Chart
  const PieTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload as SatisfactionDataItem;
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
  
  // Benutzerdefinierter Tooltip für Balkendiagramm
  const BarTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white truncate max-w-xs">{item.fullName}</p>
          <div className="mt-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">Anzahl: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {item.count}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700 dark:text-gray-300">KI-Konfidenz: </span>
              <span className="font-medium ml-2 text-gray-900 dark:text-white">
                {item.avg_confidence}%
              </span>
            </div>
          </div>
        </div>
      );
    }
    
    return null;
  };

  // Ermittle die am häufigsten vorkommende Zufriedenheit
  const mostFrequentSatisfaction = satisfactionData.reduce(
    (max: SatisfactionDataItem, item) => item.value > max.value ? item : max, 
    { name: '', value: 0, key: 'neutral' }
  );
  
  // Filter-Caption basierend auf Auswahl
  const filterCaption = selectedSatisfaction
    ? `${selectedSatisfaction === 'satisfied' || selectedSatisfaction === 'zufrieden' 
        ? 'Zufriedene' 
        : selectedSatisfaction === 'not_satisfied' 
        ? 'Unzufriedene' 
        : 'Neutrale'} Kunden`
    : 'Alle Kundenbewertungen';

  return (
    <div className="h-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Kundenzufriedenheit
        </h3>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Zufriedenheits-Verteilung */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
            Verteilung der Kundenzufriedenheit
          </h4>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={satisfactionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  onClick={(data: SatisfactionDataItem) => setSelectedSatisfaction(
                    selectedSatisfaction === data.key ? null : data.key
                  )}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                >
                  {satisfactionData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={satisfactionColors[entry.key]} 
                      stroke={selectedSatisfaction === entry.key ? '#000' : '#fff'}
                      strokeWidth={selectedSatisfaction === entry.key ? 2 : 1}
                    />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2 text-sm text-gray-600 dark:text-gray-400">
            <p>
              Klicken Sie auf einen Bereich, um nach Zufriedenheit zu filtern
            </p>
            <p className="mt-1">
              {mostFrequentSatisfaction.name} macht {totalItems > 0 
                ? `${(mostFrequentSatisfaction.value / totalItems * 100).toFixed(1)}%`
                : '0%'} aller Bewertungen aus
            </p>
          </div>
        </div>

        {/* Häufigste Abbruchgründe nach Zufriedenheit */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-medium text-gray-700 dark:text-gray-300">
              Häufigste Beendigungsgründe
            </h4>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {filterCaption}
            </div>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={reasonsBySatisfactionData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  width={150}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip content={<BarTooltip />} />
                <Legend />
                <Bar 
                  dataKey="count" 
                  name="Anzahl" 
                  fill={
                    selectedSatisfaction === 'satisfied' || selectedSatisfaction === 'zufrieden'
                      ? satisfactionColors.satisfied
                      : selectedSatisfaction === 'not_satisfied'
                      ? satisfactionColors.not_satisfied
                      : '#6366f1'
                  }
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            <p>
              {reasonsBySatisfactionData.length > 0 
                ? `"${reasonsBySatisfactionData[0].fullName}" ist mit ${reasonsBySatisfactionData[0].count} Fällen der häufigste Grund.`
                : 'Keine Daten zu Abbruchgründen verfügbar.'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerSatisfactionWidget; 