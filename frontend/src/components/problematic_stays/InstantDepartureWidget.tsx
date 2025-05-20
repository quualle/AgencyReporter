import React, { useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, TooltipProps, PieChart, Pie, Sector
} from 'recharts';

interface InstantDepartureWidgetProps {
  data: any[];
  isLoading: boolean;
  detailedData?: any[]; // Neue Daten vom /instant-departures Endpunkt
}

const InstantDepartureWidget: React.FC<InstantDepartureWidgetProps> = ({ data, isLoading, detailedData }) => {
  const [activeReasonIndex, setActiveReasonIndex] = useState<number | undefined>(undefined);

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
      day: i,
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

  // Aufbereitung der Abbruchgründe für die Visualisierung
  const prepareReasonData = () => {
    if (!detailedData || detailedData.length === 0) return [];

    // Gruppiere detaillierte Daten nach Grund
    const reasonsMap = new Map();
    detailedData.forEach(item => {
      const reason = item.reason || 'Unbekannt';
      if (!reasonsMap.has(reason)) {
        reasonsMap.set(reason, {
          name: reason,
          value: 0,
          satisfaction: {
            satisfied: 0,
            not_satisfied: 0,
            neutral: 0
          },
          days: Array(9).fill(0) // Array für Tage 1-9
        });
      }
      
      const data = reasonsMap.get(reason);
      data.value += item.count;
      
      // Kundenzufriedenheit 
      if (item.customer_satisfaction === 'satisfied' || item.customer_satisfaction === 'zufrieden') {
        data.satisfaction.satisfied += item.count;
      } else if (item.customer_satisfaction === 'not_satisfied') {
        data.satisfaction.not_satisfied += item.count;
      } else {
        data.satisfaction.neutral += item.count;
      }
      
      // Tage zählen, wenn instant_departure_after vorhanden ist
      if (item.instant_departure_after && item.instant_departure_after <= 9) {
        data.days[item.instant_departure_after - 1] += item.count;
      }
    });
    
    // Konvertiere Map zu Array und sortiere nach Häufigkeit
    return Array.from(reasonsMap.values())
      .sort((a, b) => b.value - a.value);
  };

  const reasonData = prepareReasonData();

  // Benutzerdefinierte Tooltip-Komponente für das Balkendiagramm
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const value = payload[0].value as number;
      const percentage = totalInstantDepartures > 0 ? (value / totalInstantDepartures * 100).toFixed(1) : '0';
      
      // Wenn detaillierte Daten verfügbar sind, zeige die häufigsten Gründe für diesen Tag
      let reasonsForDay = null;
      if (detailedData && detailedData.length > 0) {
        const day = parseInt(label.split(' ')[0]);
        const reasonsForThisDay = detailedData
          .filter(item => item.instant_departure_after === day)
          .sort((a, b) => b.count - a.count)
          .slice(0, 3); // Top 3 Gründe
          
        if (reasonsForThisDay.length > 0) {
          reasonsForDay = (
            <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
              <p className="font-medium text-sm text-gray-900 dark:text-white">Top Gründe:</p>
              {reasonsForThisDay.map((reason, idx) => (
                <div key={idx} className="flex justify-between mt-1 text-sm">
                  <span className="text-gray-700 dark:text-gray-300 truncate max-w-[120px]">{reason.reason}</span>
                  <span className="font-medium text-gray-900 dark:text-white">{reason.count}</span>
                </div>
              ))}
            </div>
          );
        }
      }
      
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
          {reasonsForDay}
        </div>
      );
    }
    
    return null;
  };

  // Aktiver Abschnitt für Pie-Chart
  const renderActiveShape = (props: any) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle,
      fill, payload, percent, value } = props;
    const sin = Math.sin(-midAngle * Math.PI / 180);
    const cos = Math.cos(-midAngle * Math.PI / 180);
    const sx = cx + (outerRadius + 10) * cos;
    const sy = cy + (outerRadius + 10) * sin;
    const mx = cx + (outerRadius + 30) * cos;
    const my = cy + (outerRadius + 30) * sin;
    const ex = mx + (cos >= 0 ? 1 : -1) * 22;
    const ey = my;
    const textAnchor = cos >= 0 ? 'start' : 'end';
  
    return (
      <g>
        <Sector
          cx={cx}
          cy={cy}
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
        />
        <Sector
          cx={cx}
          cy={cy}
          startAngle={startAngle}
          endAngle={endAngle}
          innerRadius={outerRadius + 6}
          outerRadius={outerRadius + 10}
          fill={fill}
        />
        <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
        <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
        <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333" className="text-[8px] md:text-xs">
          {payload.name.length > 25 ? payload.name.substring(0, 23) + "..." : payload.name}
        </text>
        <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={16} textAnchor={textAnchor} fill="#999" className="text-[8px] md:text-xs">
          {`${value} (${(percent * 100).toFixed(1)}%)`}
        </text>
      </g>
    );
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

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
            Verteilung nach Tagen
          </h4>
          <div className="h-[320px] w-full">
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

        {reasonData.length > 0 && (
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
              Häufigste Beendigungsgründe
            </h4>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    activeIndex={activeReasonIndex}
                    activeShape={renderActiveShape}
                    data={reasonData.slice(0, 8)} // Top 8 Gründe
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    onMouseEnter={(_, index) => setActiveReasonIndex(index)}
                    onMouseLeave={() => setActiveReasonIndex(undefined)}
                  >
                    {reasonData.slice(0, 8).map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899', '#64748b'][index % 8]} 
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              <p>
                {reasonData.length > 0 
                  ? `"${reasonData[0].name}" ist mit ${reasonData[0].value} Fällen (${(reasonData[0].value / totalInstantDepartures * 100).toFixed(1)}%) der häufigste Grund.`
                  : 'Keine Daten zu Abbruchgründen verfügbar.'
                }
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InstantDepartureWidget; 