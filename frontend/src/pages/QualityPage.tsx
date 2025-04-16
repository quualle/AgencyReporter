import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService, { ProfileQualityData, ComparisonData } from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

interface ViolationCategory {
  name: string;
  key: string;
  value: number;
  rate: number;
  industry_avg: number;
}

const QualityPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  const [profileData, setProfileData] = useState<ProfileQualityData | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [violationCategories, setViolationCategories] = useState<ViolationCategory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch data in parallel
        const [profileResponse, comparisonResponse] = await Promise.all([
          apiService.getAgencyProfileQuality(selectedAgency.agency_id, timePeriod),
          apiService.compareAgencyProfileQuality(selectedAgency.agency_id, timePeriod)
        ]);
        
        setProfileData(profileResponse);
        setComparisonData(comparisonResponse);
        
        // Prepare violation categories for visualization
        if (profileResponse && comparisonResponse) {
          const categories: ViolationCategory[] = [
            {
              name: 'Erfahrung',
              key: 'experience',
              value: profileResponse.experience_violations || 0,
              rate: profileResponse.experience_violation_rate || 0,
              industry_avg: comparisonResponse.industry_average.experience_violation_rate || 0
            },
            {
              name: 'Sprachkenntnisse',
              key: 'language',
              value: profileResponse.language_violations || 0,
              rate: profileResponse.language_violation_rate || 0,
              industry_avg: comparisonResponse.industry_average.language_violation_rate || 0
            },
            {
              name: 'Raucher-Status',
              key: 'smoker',
              value: profileResponse.smoker_violations || 0,
              rate: profileResponse.smoker_violation_rate || 0,
              industry_avg: comparisonResponse.industry_average.smoker_violation_rate || 0
            },
            {
              name: 'Alter',
              key: 'age',
              value: profileResponse.age_violations || 0,
              rate: profileResponse.age_violation_rate || 0,
              industry_avg: comparisonResponse.industry_average.age_violation_rate || 0
            },
            {
              name: 'Führerschein',
              key: 'license',
              value: profileResponse.license_violations || 0,
              rate: profileResponse.license_violation_rate || 0,
              industry_avg: comparisonResponse.industry_average.license_violation_rate || 0
            }
          ];
          
          setViolationCategories(categories);
        }
      } catch (err) {
        console.error('Error fetching profile quality data:', err);
        setError('Fehler beim Laden der Profilqualitäts-Daten. Bitte versuchen Sie es später erneut.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getViolationColor = (rate: number) => {
    if (rate < 0.05) return '#10b981'; // Low violations - green
    if (rate < 0.15) return '#f59e0b'; // Medium violations - yellow/amber
    return '#ef4444'; // High violations - red
  };

  const getHeatmapData = () => {
    if (!violationCategories.length) return [];
    
    // Transform data for heatmap visualization
    return violationCategories.map(category => ({
      name: category.name,
      value: category.rate,
      fill: getViolationColor(category.rate)
    }));
  };

  const getRadarData = () => {
    if (!violationCategories.length) return [];
    
    // Transform data for radar chart
    // Using inverse of violation rate (1 - rate) so higher values are better
    return violationCategories.map(category => ({
      subject: category.name,
      agency: 1 - category.rate,
      industry: 1 - category.industry_avg,
      fullMark: 1
    }));
  };

  if (isLoading) {
    return <Loading message="Profilqualitäts-Daten werden geladen..." />;
  }

  if (error) {
    return <ErrorMessage message={error} retry={() => setIsLoading(true)} />;
  }

  if (!selectedAgency) {
    return (
      <div className="text-center p-8">
        <h2 className="text-xl font-semibold mb-4">Keine Agentur ausgewählt</h2>
        <p className="text-gray-600 dark:text-gray-300">Bitte wählen Sie eine Agentur aus dem Dropdown-Menü.</p>
      </div>
    );
  }

  return (
    <div className="quality-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
          Profilqualität: {selectedAgency.agency_name}
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Analyse der Profilgenauigkeit und Regelverstöße bei Betreuungskräften
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Total Profile Quality Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Gesamtqualität</h2>
          
          <div className="flex items-center justify-center mb-4">
            <div 
              className="relative w-40 h-40 rounded-full flex items-center justify-center text-2xl font-bold"
              style={{
                background: `conic-gradient(
                  ${getViolationColor(
                    violationCategories.reduce((sum, cat) => sum + cat.rate, 0) / violationCategories.length
                  )} ${(violationCategories.reduce((sum, cat) => sum + cat.rate, 0) / violationCategories.length) * 360}deg,
                  #e5e7eb ${(violationCategories.reduce((sum, cat) => sum + cat.rate, 0) / violationCategories.length) * 360}deg 360deg
                )`
              }}
            >
              <div className="absolute inset-3 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center">
                <span className="text-gray-800 dark:text-white">
                  {formatPercentage(1 - (violationCategories.reduce((sum, cat) => sum + cat.rate, 0) / violationCategories.length))}
                </span>
              </div>
            </div>
          </div>
          
          <p className="text-center text-gray-600 dark:text-gray-300">
            Übereinstimmung zwischen Profilangaben und realer Wahrnehmung
          </p>

          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">Geprüfte Profile:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {profileData?.total_caregivers || 0}
              </span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-gray-600 dark:text-gray-300">Durchschn. Regelverstoß-Rate:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {formatPercentage(violationCategories.reduce((sum, cat) => sum + cat.rate, 0) / violationCategories.length)}
              </span>
            </div>
          </div>
        </div>

        {/* Comparison with Industry Average */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Branchen-Vergleich</h2>
          
          <div className="space-y-4">
            {violationCategories.map((category) => (
              <div key={category.key} className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">{category.name}:</span>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-800 dark:text-white">
                    {formatPercentage(category.rate)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    vs. {formatPercentage(category.industry_avg)}
                  </span>
                  <span className={`text-xs ${
                    category.rate < category.industry_avg ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {category.rate < category.industry_avg ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-md font-semibold mb-2 text-gray-800 dark:text-white">Gesamtvergleich</h3>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">Qualitätsrang:</span>
              <span className="font-medium text-gray-800 dark:text-white">
                {comparisonData ? 
                  `${comparisonData.all_agencies.findIndex(a => a.agency_id === selectedAgency.agency_id) + 1} von ${comparisonData.all_agencies.length}` :
                  'N/A'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Detailed Violations */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Regelverstöße nach Kategorie</h2>
          
          <div className="space-y-4">
            {violationCategories.map((category) => (
              <div key={category.key} className="flex flex-col">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-gray-600 dark:text-gray-300">{category.name}:</span>
                  <span className="font-medium text-gray-800 dark:text-white">
                    {category.value} Verstöße ({formatPercentage(category.rate)})
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                  <div 
                    className="h-2.5 rounded-full" 
                    style={{ 
                      width: `${category.rate * 100}%`,
                      backgroundColor: getViolationColor(category.rate)
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Radar Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Qualitätsvergleich</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Radar-Diagramm zum Vergleich der Profilqualität in verschiedenen Kategorien. 
            Höhere Werte bedeuten weniger Regelverstöße.
          </p>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart outerRadius={90} data={getRadarData()}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis 
                  angle={30} 
                  domain={[0, 1]} 
                  tickFormatter={(value) => formatPercentage(value)}
                />
                <Radar
                  name={selectedAgency.agency_name}
                  dataKey="agency"
                  stroke="#4f46e5"
                  fill="#4f46e5"
                  fillOpacity={0.6}
                />
                <Radar
                  name="Branchendurchschnitt"
                  dataKey="industry"
                  stroke="#9ca3af"
                  fill="#9ca3af"
                  fillOpacity={0.3}
                />
                <Tooltip 
                  formatter={(value: number) => [formatPercentage(value), 'Qualitätsrate']}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Violation Rates Bar Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Regelverstoß-Übersicht</h2>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            Vergleich der Regelverstoß-Raten nach Kategorie zwischen der Agentur und dem Branchendurchschnitt.
          </p>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={violationCategories}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  domain={[0, 0.3]} 
                  tickFormatter={(value) => formatPercentage(value)}
                />
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  width={120}
                />
                <Tooltip 
                  formatter={(value: number) => [formatPercentage(value), 'Regelverstoß-Rate']}
                  labelFormatter={(label) => `Kategorie: ${label}`}
                />
                <Legend />
                <Bar 
                  dataKey="rate" 
                  name={selectedAgency.agency_name} 
                  stackId="a"
                >
                  {violationCategories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getViolationColor(entry.rate)} />
                  ))}
                </Bar>
                <Bar 
                  dataKey="industry_avg" 
                  name="Branchendurchschnitt" 
                  fill="#9ca3af" 
                  stackId="b" 
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Heatmap of Problem Areas */}
      <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Heatmap der Problembereiche</h2>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
          Visuelle Darstellung der Problembereiche bei Profilangaben. 
          Rot zeigt Bereiche mit hohen Regelverstoß-Raten, Grün Bereiche mit niedrigen Raten.
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-6">
          {getHeatmapData().map((item, index) => (
            <div 
              key={index}
              className="aspect-square rounded-lg flex flex-col items-center justify-center p-4 text-white"
              style={{ backgroundColor: item.fill }}
            >
              <span className="text-lg font-semibold mb-2">{item.name}</span>
              <span className="text-2xl font-bold">{formatPercentage(item.value)}</span>
              <span className="text-sm mt-2">Regelverstoß-Rate</span>
            </div>
          ))}
        </div>
        
        <div className="flex justify-center items-center mt-8">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded mr-2" />
              <span className="text-sm text-gray-600 dark:text-gray-300">&lt; 5% Verstöße</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-amber-500 rounded mr-2" />
              <span className="text-sm text-gray-600 dark:text-gray-300">5% - 15% Verstöße</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-500 rounded mr-2" />
              <span className="text-sm text-gray-600 dark:text-gray-300">&gt; 15% Verstöße</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QualityPage; 