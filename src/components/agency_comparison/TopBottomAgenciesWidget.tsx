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

interface TopBottomAgenciesWidgetProps {
  data: any[];
  isLoading: boolean;
  showTop: boolean;
  limit: number;
}

const TopBottomAgenciesWidget: React.FC<TopBottomAgenciesWidgetProps> = ({ 
  data, 
  isLoading, 
  showTop = true, 
  limit = 5 
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

  // Sort data by deployment days
  // For top agencies: descending order
  // For bottom agencies: ascending order
  const sortedData = [...data].sort((a, b) => {
    return showTop 
      ? b.deployment_days - a.deployment_days 
      : a.deployment_days - b.deployment_days;
  }).slice(0, limit);

  // Prepare chart data
  const chartData = {
    labels: sortedData.map(agency => agency.agency_name),
    datasets: [
      {
        label: 'Einsatztage',
        data: sortedData.map(agency => agency.deployment_days),
        backgroundColor: showTop ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)',
        borderColor: showTop ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)',
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
            return `${context.raw} Tage`;
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
      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
          {showTop ? 'Agenturen mit den meisten Einsatztagen' : 'Agenturen mit den wenigsten Einsatztagen'}
        </p>
      </div>
    </div>
  );
};

export default TopBottomAgenciesWidget; 