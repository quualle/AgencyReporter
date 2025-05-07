import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  Tooltip, 
  XAxis, 
  YAxis, 
  Treemap, 
  Rectangle,
  TooltipProps,
  Legend,
  Cell
} from 'recharts';

interface ReasonHeatmapWidgetProps {
  data: any[];
  isLoading: boolean;
}

interface FormattedDataItem {
  name: string;
  agency: string;
  agency_id: string;
  value: number;
  percentage: number;
  event_type: string;
  color: string;
}

const ReasonHeatmapWidget: React.FC<ReasonHeatmapWidgetProps> = ({ data, isLoading }) => {
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="h-96 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"></div>
    );
  }

  // Farben für die Heatmap, nach Häufigkeit
  const colors = [
    '#eaeff8', // sehr selten
    '#d0e0f7', // selten
    '#91B3FA', // gelegentlich
    '#6F96F4', // häufig
    '#4f46e5', // sehr häufig
  ];

  // Farben für die Event-Typen
  const eventTypeColors = {
    'cancelled_before_arrival': '#ef4444', // rot für Abbrüche vor Anreise
    'shortened_after_arrival': '#f59e0b'   // orange für Verkürzungen nach Anreise
  };

  // Daten für Heatmap formatieren
  const formatDataForHeatmap = (): FormattedDataItem[] => {
    const formattedData: FormattedDataItem[] = [];
    
    data.forEach(item => {
      // Filter anwenden, wenn gewählt
      if (eventTypeFilter !== 'all' && item.event_type !== eventTypeFilter) {
        return;
      }
      
      // Farbindex basierend auf Prozentsatz bestimmen
      let colorIndex = 0;
      if (item.percentage > 50) colorIndex = 4;
      else if (item.percentage > 30) colorIndex = 3;
      else if (item.percentage > 15) colorIndex = 2;
      else if (item.percentage > 5) colorIndex = 1;
      
      formattedData.push({
        name: item.reason,
        agency: item.agency_name,
        agency_id: item.agency_id,
        value: item.count,
        percentage: item.percentage,
        event_type: item.event_type,
        color: colors[colorIndex]
      });
    });
    
    // Nach Wert sortieren, höchste zuerst
    return formattedData.sort((a, b) => b.value - a.value);
  };

  const heatmapData = formatDataForHeatmap();
  
  // Benutzerdefinierte Tooltip-Komponente
  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload as FormattedDataItem;
      const eventTypeLabel = item.event_type === 'cancelled_before_arrival' 
        ? 'Abbruch vor Anreise' 
        : 'Verkürzung nach Anreise';
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-medium text-gray-900 dark:text-white truncate max-w-xs">{item.name}</p>
          <div className="mt-2">
            <p className="text-gray-700 dark:text-gray-300">
              <span className="font-semibold">Agentur:</span> {item.agency}
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <span className="font-semibold">Typ:</span> {eventTypeLabel}
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <span className="font-semibold">Anzahl:</span> {item.value}
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              <span className="font-semibold">Anteil:</span> {item.percentage.toFixed(1)}%
            </p>
          </div>
        </div>
      );
    }
    
    return null;
  };

  // Benutzerdefinierte rechteckige Zelle für die Heatmap
  const CustomizedContent = (props: any) => {
    const { x, y, width, height, root, depth, name, color, value } = props;
    
    return (
      <g>
        <Rectangle
          x={x}
          y={y}
          width={width}
          height={height}
          fill={color}
          stroke="#fff"
          strokeWidth={2}
        />
        {depth === 1 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 12}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-gray-800 dark:fill-white font-medium text-[10px] md:text-xs"
            >
              {name.length > 20 ? name.substring(0, 18) + "..." : name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 8}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-gray-700 dark:fill-gray-300 text-[9px] md:text-xs"
            >
              {value}
            </text>
          </>
        )}
      </g>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Verteilung der Abbruchgründe
        </h3>
        <div>
          <select 
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            <option value="all">Alle Typen</option>
            <option value="cancelled_before_arrival">Vor Anreise</option>
            <option value="shortened_after_arrival">Nach Anreise</option>
          </select>
        </div>
      </div>
      
      <div className="flex-1 h-96">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={heatmapData}
            dataKey="value"
            stroke="#fff"
            content={<CustomizedContent />}
          >
            <Tooltip content={<CustomTooltip />} />
          </Treemap>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 flex flex-wrap justify-center gap-4">
        <div className="flex items-center">
          <div className="w-3 h-3 mr-1 bg-[#eaeff8] border border-gray-300"></div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Sehr selten (&lt;5%)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 mr-1 bg-[#d0e0f7] border border-gray-300"></div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Selten (5-15%)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 mr-1 bg-[#91B3FA] border border-gray-300"></div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Gelegentlich (15-30%)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 mr-1 bg-[#6F96F4] border border-gray-300"></div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Häufig (30-50%)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 mr-1 bg-[#4f46e5] border border-gray-300"></div>
          <span className="text-xs text-gray-600 dark:text-gray-400">Sehr häufig (&gt;50%)</span>
        </div>
      </div>
    </div>
  );
};

export default ReasonHeatmapWidget; 