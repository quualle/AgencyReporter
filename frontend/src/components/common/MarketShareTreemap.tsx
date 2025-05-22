import React, { useState, useEffect } from 'react';
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts';

interface TreemapData {
  name: string;
  agency_id: string;
  size: number;
  colorIndex?: number;
}

interface MarketShareTreemapProps {
  data: Array<{
    agency_id: string;
    agency_name: string;
    total_carestays: number;
    [key: string]: any;
  }>;
  isLoading: boolean;
  totalLabel?: string;
  onAgencyClick?: (agencyId: string, agencyName: string) => void;
}

const COLORS = [
  '#4299E1', // blue-500
  '#4FD1C5', // teal-400
  '#48BB78', // green-500
  '#38B2AC', // teal-500
  '#3182CE', // blue-600
  '#2C7A7B', // teal-700
  '#2F855A', // green-700
  '#2B6CB0', // blue-700
  '#276749', // green-800
  '#2C5282', // blue-800
  '#1A365D', // blue-900
  '#1A4E2B', // green-900
];

const MarketShareTreemap: React.FC<MarketShareTreemapProps> = ({
  data,
  isLoading,
  totalLabel = 'Einsätze',
  onAgencyClick
}) => {
  const [treemapData, setTreemapData] = useState<TreemapData[]>([]);
  const [totalCareStays, setTotalCareStays] = useState<number>(0);

  useEffect(() => {
    if (!data || data.length === 0) {
      setTreemapData([]);
      setTotalCareStays(0);
      return;
    }

    // Calculate total across all agencies for percentage calculation
    const total = data.reduce((acc, curr) => acc + (curr.total_carestays || 0), 0);
    setTotalCareStays(total);

    // Sort by total care stays (largest first)
    const sortedData = [...data].sort((a, b) => 
      (b.total_carestays || 0) - (a.total_carestays || 0)
    );

    // Transform to treemap format
    const mappedData = sortedData.map((agency, index) => ({
      name: agency.agency_name,
      agency_id: agency.agency_id,
      size: agency.total_carestays || 0,
      colorIndex: index % COLORS.length
    }));

    setTreemapData(mappedData);
  }, [data]);

  const formatPercentage = (value: number): string => {
    return totalCareStays > 0 ? `${((value / totalCareStays) * 100).toFixed(1)}%` : '0%';
  };

  const formatNumber = (value: number): string => {
    return value.toLocaleString();
  };

  // Custom tooltip component for treemap
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded shadow-lg">
          <p className="font-bold text-gray-800 dark:text-gray-200">{data.name}</p>
          <p className="text-gray-600 dark:text-gray-400">
            {formatNumber(data.size)} {totalLabel}
          </p>
          <p className="text-gray-600 dark:text-gray-400">
            Marktanteil: {formatPercentage(data.size)}
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom content for treemap node
  const CustomTreemapContent = (props: any) => {
    const { x, y, width, height, index, name, size } = props;
    
    // Don't render if area is too small
    if (width < 40 || height < 40) return null;
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: COLORS[props.colorIndex || 0],
            stroke: '#fff',
            strokeWidth: 2,
            cursor: 'pointer'
          }}
          onClick={() => onAgencyClick && onAgencyClick(props.agency_id, name)}
        />
        <text
          x={x + width / 2}
          y={y + height / 2 - 8}
          textAnchor="middle"
          fill="#fff"
          fontSize={width < 60 ? 10 : 12}
          fontWeight="bold"
          style={{ pointerEvents: 'none' }}
        >
          {name}
        </text>
        <text
          x={x + width / 2}
          y={y + height / 2 + 8}
          textAnchor="middle"
          fill="#fff"
          fontSize={width < 60 ? 9 : 11}
          style={{ pointerEvents: 'none' }}
        >
          {formatPercentage(size)}
        </text>
      </g>
    );
  };

  if (isLoading) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm animate-pulse h-[500px]">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
        <div className="h-full bg-gray-100 dark:bg-gray-700 rounded"></div>
      </div>
    );
  }

  if (treemapData.length === 0) {
    return (
      <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm h-[500px]">
        <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Marktanteile nach Einsatzvolumen</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Keine Daten verfügbar</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm h-[500px]">
      <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Marktanteile nach Einsatzvolumen</h3>
      
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Gesamtvolumen: {formatNumber(totalCareStays)} {totalLabel} · Klicken Sie auf eine Agentur für Details
      </div>
      
      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={treemapData}
            dataKey="size"
            aspectRatio={1}
            stroke="#fff"
            content={<CustomTreemapContent />}
          >
            <Tooltip content={<CustomTooltip />} />
          </Treemap>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MarketShareTreemap;