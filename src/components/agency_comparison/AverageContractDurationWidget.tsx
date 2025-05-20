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

interface AverageContractDurationWidgetProps {
  data: any[];
  isLoading: boolean;
  limit?: number;
}

const AverageContractDurationWidget: React.FC<AverageContractDurationWidgetProps> = ({ 
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

  // Sort data by average contract duration in descending order
  const sortedData = [...data]
    .sort((a, b) => b.avg_contract_duration - a.avg_contract_duration)
    .slice(0, limit);

  // Calculate the industry average for comparison
  const industryAverage = data.reduce((sum, agency) => sum + agency.avg_contract_duration, 0) / data.length;

  // Prepare chart data
  const chartData = {
    labels: sortedData.map(agency => agency.agency_name),
    datasets: [
      {
        label: 'Durchschnittliche Vertragsdauer (Tage)',
        data: sortedData.map(agency => agency.avg_contract_duration),
        backgroundColor: sortedData.map(agency => 
          agency.avg_contract_duration > industryAverage 
            ? 'rgba(34, 197, 94, 0.8)' 
            : 'rgba(239, 68, 68, 0.8)'
        ),
        borderColor: sortedData.map(agency => 
          agency.avg_contract_duration > industryAverage 
            ? 'rgb(34, 197, 94)' 
            : 'rgb(239, 68, 68)'
        ),
        borderWidth: 1,
      },
    ],
  };

  // Chart options
  const options: ChartOptions<'bar'> = {
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
            return `${value.toFixed(1)} Tage`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.05)',
        },
      }
    },
  };

  return (
    <div>
      <div className="mb-4">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Branchendurchschnitt:
          </span>
          <span className="text-sm font-bold text-gray-800 dark:text-white">
            {industryAverage.toFixed(1)} Tage
          </span>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Gemessen über mehrere Carestays des gleichen Kunden/Leads
        </div>
      </div>
      
      <div className="h-80">
        <Bar data={chartData} options={options} />
      </div>
      
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Grün = über Branchendurchschnitt, Rot = unter Branchendurchschnitt
        </p>
      </div>

      <div className="mt-6">
        <h3 className="text-md font-semibold text-gray-800 dark:text-white mb-2">Hinweis zur Berechnung:</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Die durchschnittliche Vertragsdauer berücksichtigt alle Carestays eines Kunden/Leads bei derselben Agentur. 
          Längere Vertragsdauern deuten auf höhere Kundenzufriedenheit und geringere Fluktuation hin.
        </p>
      </div>
    </div>
  );
};

export default AverageContractDurationWidget; 