import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';

// Register the required chart components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ProblematicStaysRatioWidgetProps {
  data: any[];
  isLoading: boolean;
  limit?: number;
}

const ProblematicStaysRatioWidget: React.FC<ProblematicStaysRatioWidgetProps> = ({ 
  data, 
  isLoading, 
  limit = 10
}) => {
  // Handle loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-gray-500 dark:text-gray-400">Keine Daten verfügbar</p>
      </div>
    );
  }

  // Sort data by problematic stays ratio (best agencies = lowest ratio first)
  const sortedBestData = [...data]
    .sort((a, b) => a.problematic_stays_ratio - b.problematic_stays_ratio)
    .slice(0, limit);

  // Sort data by problematic stays ratio (worst agencies = highest ratio first)
  const sortedWorstData = [...data]
    .sort((a, b) => b.problematic_stays_ratio - a.problematic_stays_ratio)
    .slice(0, limit);

  // Calculate the industry average for comparison
  const industryAverage = data.reduce((sum, agency) => sum + agency.problematic_stays_ratio, 0) / data.length;

  // Prepare chart data for best agencies
  const bestChartData = {
    labels: sortedBestData.map(agency => agency.agency_name),
    datasets: [
      {
        label: 'Problematische Einsätze (%)',
        data: sortedBestData.map(agency => (agency.problematic_stays_ratio * 100).toFixed(1)),
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
      },
    ],
  };

  // Prepare chart data for worst agencies
  const worstChartData = {
    labels: sortedWorstData.map(agency => agency.agency_name),
    datasets: [
      {
        label: 'Problematische Einsätze (%)',
        data: sortedWorstData.map(agency => (agency.problematic_stays_ratio * 100).toFixed(1)),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1,
      },
    ],
  };

  // Chart options
  const options: ChartOptions<'bar'> = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.raw as number;
            return `${value}%`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      },
      y: {
        grid: {
          display: false,
        },
      }
    },
  };

  return (
    <div>
      <div className="mb-4">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Branchendurchschnitt problematischer Einsätze:
          </span>
          <span className="text-sm font-bold text-gray-800 dark:text-white">
            {(industryAverage * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Best Agencies */}
        <div>
          <h3 className="text-md font-semibold text-gray-800 dark:text-white mb-4 text-center">
            Top-Agenturen: Geringster Anteil problematischer Einsätze
          </h3>
          <div className="h-96">
            <Bar data={bestChartData} options={options} />
          </div>
        </div>

        {/* Worst Agencies */}
        <div>
          <h3 className="text-md font-semibold text-gray-800 dark:text-white mb-4 text-center">
            Flop-Agenturen: Höchster Anteil problematischer Einsätze
          </h3>
          <div className="h-96">
            <Bar data={worstChartData} options={options} />
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <h3 className="text-md font-semibold text-gray-800 dark:text-white mb-2">Was sind "problematische Einsätze"?</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Als problematische Einsätze werden gewertet: 
        </p>
        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 mt-2">
          <li>Einsätze, die vor Anreise abgebrochen wurden</li>
          <li>Einsätze, die nach Anreise um mehr als 14 Tage verkürzt wurden</li>
          <li>Einsätze, die innerhalb von 10 Tagen nach Anreise beendet wurden ("sofortige Abreisen")</li>
        </ul>
      </div>
    </div>
  );
};

export default ProblematicStaysRatioWidget; 