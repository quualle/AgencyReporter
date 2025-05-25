import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

// Eigene Icon-Komponenten anstelle von react-icons
const IconArrowUp = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-red-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
  </svg>
);

const IconArrowDown = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
  </svg>
);

const IconEquals = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-500 ml-1" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4 9h12a1 1 0 010 2H4a1 1 0 110-2zm0-4h12a1 1 0 110 2H4a1 1 0 010-2z" clipRule="evenodd" />
  </svg>
);

interface OverviewWidgetProps {
  data: any[];
  isLoading: boolean;
}

const OverviewWidget: React.FC<OverviewWidgetProps> = ({ data, isLoading }) => {
  // Debug logging
  console.log('OverviewWidget received:', { data, isLoading, dataLength: data?.length });
  
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    console.log('OverviewWidget showing gray skeleton:', { isLoading, hasData: !!data, dataLength: data?.length });
    return (
      <div className="animate-pulse">
        <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-48 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-36"></div>
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-36"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-32"></div>
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-32"></div>
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-32"></div>
        </div>
      </div>
    );
  }

  // Daten aus dem ersten Element extrahieren (wir erwarten nur ein Element im Array)
  const stats = data[0];

  // Berechnungen der Prozentwerte in Bezug auf problematische Einsätze statt aller Einsätze
  const cancelledPercentageOfProblematic = stats.total_problematic > 0 
    ? (stats.cancelled_before_arrival_count / stats.total_problematic) * 100 
    : 0;
    
  const shortenedPercentageOfProblematic = stats.total_problematic > 0 
    ? (stats.shortened_after_arrival_count / stats.total_problematic) * 100 
    : 0;
    
  const instantDeparturePercentageOfProblematic = stats.total_problematic > 0 
    ? (stats.instant_departure_count / stats.total_problematic) * 100 
    : 0;
    
  const replacementPercentageOfProblematic = stats.total_problematic > 0 
    ? (stats.with_replacement_count / stats.total_problematic) * 100 
    : 0;
    
  const satisfiedPercentageOfProblematic = stats.total_problematic > 0 
    ? (stats.satisfied_count / stats.total_problematic) * 100 
    : 0;

  // Trend-Indikator-Komponente
  const TrendIndicator = ({ value }: { value: number }) => {
    if (value > 0) {
      return <IconArrowUp />; // Steigend ist negativ
    } else if (value < 0) {
      return <IconArrowDown />; // Fallend ist positiv
    } else {
      return <IconEquals />; // Gleichbleibend
    }
  };

  // Vergleichswert-Komponente
  const ComparisonValue = ({ value, comparisonValue }: { value: number, comparisonValue: number }) => {
    const difference = value - comparisonValue;
    const percentageDifference = comparisonValue !== 0 ? (difference / comparisonValue) * 100 : 0;
    
    return (
      <div className="flex items-center justify-center mt-1 text-sm">
        <span className="text-gray-500 dark:text-gray-400">vs. Durchschnitt: </span>
        <span className={`font-medium ml-1 ${difference > 0 ? 'text-red-500' : difference < 0 ? 'text-green-500' : 'text-gray-500'}`}>
          {comparisonValue !== 0 ? `${Math.abs(percentageDifference).toFixed(1)}%` : 'N/A'}
        </span>
        <TrendIndicator value={difference} />
      </div>
    );
  };

  // Haupt-Metrik-Karte-Komponente
  const MainKpiCard = ({ 
    title, 
    value, 
    comparisonValue = 0,
    format = 'percentage',
    description = ''
  }: { 
    title: string, 
    value: number, 
    comparisonValue?: number,
    format?: 'percentage' | 'number' | 'days',
    description?: string
  }) => {
    let formattedValue: string;
    
    switch (format) {
      case 'percentage':
        formattedValue = `${value.toFixed(1)}%`;
        break;
      case 'days':
        formattedValue = `${value.toFixed(1)} Tage`;
        break;
      case 'number':
      default:
        formattedValue = value.toFixed(0);
    }
    
    return (
      <div className="bg-gradient-to-br from-emerald-50 to-teal-100 dark:from-emerald-900 dark:to-teal-800 border-2 border-emerald-200 dark:border-emerald-700 rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-emerald-700 dark:text-emerald-300 text-center">{title}</h3>
        <div className="mt-3 flex items-baseline justify-center">
          <span className="text-3xl font-bold text-emerald-800 dark:text-emerald-200">
            {formattedValue}
          </span>
        </div>
        {description && (
          <p className="mt-2 text-sm text-emerald-600 dark:text-emerald-400 text-center">{description}</p>
        )}
        {comparisonValue !== undefined && <ComparisonValue value={value} comparisonValue={comparisonValue} />}
      </div>
    );
  };

  // Untergeordnete-Metrik-Karte-Komponente
  const SubKpiCard = ({ 
    title, 
    value, 
    comparisonValue = 0,
    format = 'percentage',
    description = '',
    bgColorClass = 'bg-blue-50 dark:bg-blue-900',
    borderColorClass = 'border-blue-200 dark:border-blue-700',
    textColorClass = 'text-blue-700 dark:text-blue-300',
    valueColorClass = 'text-blue-800 dark:text-blue-200'
  }: { 
    title: string, 
    value: number, 
    comparisonValue?: number,
    format?: 'percentage' | 'number' | 'days',
    description?: string,
    bgColorClass?: string,
    borderColorClass?: string,
    textColorClass?: string,
    valueColorClass?: string
  }) => {
    let formattedValue: string;
    
    switch (format) {
      case 'percentage':
        formattedValue = `${value.toFixed(1)}%`;
        break;
      case 'days':
        formattedValue = `${value.toFixed(1)} Tage`;
        break;
      case 'number':
      default:
        formattedValue = value.toFixed(0);
    }
    
    return (
      <div className={`${bgColorClass} border border-l-4 ${borderColorClass} rounded-lg shadow p-4`}>
        <h3 className={`text-sm font-medium ${textColorClass} text-center`}>{title}</h3>
        <div className="mt-2 flex items-baseline justify-center">
          <span className={`text-2xl font-bold ${valueColorClass}`}>
            {formattedValue}
          </span>
        </div>
        {description && (
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 text-center">{description}</p>
        )}
        {comparisonValue !== undefined && <ComparisonValue value={value} comparisonValue={comparisonValue} />}
      </div>
    );
  };

  // Erklärende-Metrik-Karte-Komponente
  const ExplanationKpiCard = ({ 
    title, 
    value, 
    format = 'percentage',
    description = '',
    bgColorClass = 'bg-gray-50 dark:bg-gray-800',
    borderColorClass = 'border-gray-200 dark:border-gray-700',
    textColorClass = 'text-gray-700 dark:text-gray-300',
    valueColorClass = 'text-gray-800 dark:text-gray-200'
  }: { 
    title: string, 
    value: number, 
    format?: 'percentage' | 'number' | 'days',
    description?: string,
    bgColorClass?: string,
    borderColorClass?: string,
    textColorClass?: string,
    valueColorClass?: string
  }) => {
    let formattedValue: string;
    
    switch (format) {
      case 'percentage':
        formattedValue = `${value.toFixed(1)}%`;
        break;
      case 'days':
        formattedValue = `${value.toFixed(1)} Tage`;
        break;
      case 'number':
      default:
        formattedValue = value.toFixed(0);
    }
    
    return (
      <div className={`${bgColorClass} border ${borderColorClass} rounded-lg shadow p-3`}>
        <h3 className={`text-xs font-medium ${textColorClass} text-center`}>{title}</h3>
        <div className="mt-1 flex items-baseline justify-center">
          <span className={`text-xl font-bold ${valueColorClass}`}>
            {formattedValue}
          </span>
        </div>
        {description && (
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-500 text-center">{description}</p>
        )}
      </div>
    );
  };

  // Outcome-Metrik-Karte-Komponente
  const OutcomeKpiCard = ({ 
    title, 
    value, 
    format = 'percentage',
    description = ''
  }: { 
    title: string, 
    value: number, 
    format?: 'percentage' | 'number' | 'days',
    description?: string
  }) => {
    let formattedValue: string;
    
    switch (format) {
      case 'percentage':
        formattedValue = `${value.toFixed(1)}%`;
        break;
      case 'days':
        formattedValue = `${value.toFixed(1)} Tage`;
        break;
      case 'number':
      default:
        formattedValue = value.toFixed(0);
    }

    // Daten für den Donut-Chart
    const donutData = [
      { name: 'Zufrieden', value: value, color: '#22c55e' },
      { name: 'Unzufrieden', value: 100 - value, color: '#ef4444' },
    ];
    
    return (
      <div className="bg-white dark:bg-gray-900 border border-purple-200 dark:border-purple-700 rounded-lg shadow p-4">
        <h3 className="text-sm font-medium text-purple-700 dark:text-purple-300 text-center mb-2">
          <span className="inline-block mr-1">🎯</span> {title}
        </h3>
        
        <div className="flex flex-col md:flex-row items-center justify-around">
          {/* Donut-Chart */}
          <div className="w-32 h-32">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={28}
                  outerRadius={40}
                  fill="#8884d8"
                  paddingAngle={2}
                  dataKey="value"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          {/* Textuelle Informationen */}
          <div className="text-center mt-2 md:mt-0">
            <div className="flex items-center justify-center space-x-3">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Zufrieden</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">Unzufrieden</span>
              </div>
            </div>
            
            <div className="mt-2">
              <span className="text-2xl font-bold text-indigo-800 dark:text-indigo-200">{formattedValue}</span>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mt-1">
                sind trotz Problemen zufrieden
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                {stats.satisfied_count || 0} von {stats.total_problematic || 0} Kunden
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Hauptkennzahl - Problematische Einsätze */}
      <MainKpiCard 
        title="Problematische Einsätze" 
        value={stats.problematic_percentage || 0}
        comparisonValue={0}
        description={`${stats.total_problematic || 0} von ${stats.total_carestays || 0} Einsätzen`}
      />
      
      {/* Zwei Hauptkategorien: Abbrüche vor Anreise und Vorzeitige Beendigungen */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Abbrüche vor Anreise mit Erklärungselementen */}
        <div className="space-y-3">
          <SubKpiCard 
            title="Abbrüche vor Anreise" 
            value={cancelledPercentageOfProblematic || 0}
            comparisonValue={0}
            description={`${stats.cancelled_before_arrival_count || 0} Einsätze (% aller probl. Einsätze)`}
            bgColorClass="bg-blue-50 dark:bg-blue-900"
            borderColorClass="border-blue-200 dark:border-blue-700"
            textColorClass="text-blue-700 dark:text-blue-300"
            valueColorClass="text-blue-800 dark:text-blue-200"
          />
          
          <div className="grid grid-cols-2 gap-2">
            <ExplanationKpiCard 
              title="Vorlaufzeit bei Abbrüchen" 
              value={stats.avg_days_before_arrival || 0}
              format="days"
              description="Tage vor Anreise"
              bgColorClass="bg-blue-50/70 dark:bg-blue-900/70"
              borderColorClass="border-blue-100 dark:border-blue-800"
              textColorClass="text-blue-600 dark:text-blue-400"
              valueColorClass="text-blue-700 dark:text-blue-300"
            />
            
            <ExplanationKpiCard 
              title="Ersatzbereitstellung" 
              value={replacementPercentageOfProblematic || 0}
              description={`Bei ${stats.with_replacement_count || 0} Abbrüchen`}
              bgColorClass="bg-blue-50/70 dark:bg-blue-900/70"
              borderColorClass="border-blue-100 dark:border-blue-800"
              textColorClass="text-blue-600 dark:text-blue-400"
              valueColorClass="text-blue-700 dark:text-blue-300"
            />
          </div>
        </div>
        
        {/* Vorzeitige Beendigungen mit Teilmenge und Erklärungselement */}
        <div className="space-y-3">
          <SubKpiCard 
            title="Vorzeitige Beendigungen" 
            value={shortenedPercentageOfProblematic || 0}
            comparisonValue={0}
            description={`${stats.shortened_after_arrival_count || 0} Einsätze (% aller probl. Einsätze)`}
            bgColorClass="bg-amber-50 dark:bg-amber-900"
            borderColorClass="border-amber-200 dark:border-amber-700"
            textColorClass="text-amber-700 dark:text-amber-300"
            valueColorClass="text-amber-800 dark:text-amber-200"
          />
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <SubKpiCard 
                title="Sofortige Abreisen (<10 Tage)" 
                value={instantDeparturePercentageOfProblematic || 0}
                description={`${stats.instant_departure_count || 0} Einsätze`}
                bgColorClass="bg-amber-50/80 dark:bg-amber-900/80"
                borderColorClass="border-amber-100 dark:border-amber-800"
                textColorClass="text-amber-600 dark:text-amber-400"
                valueColorClass="text-amber-700 dark:text-amber-300"
              />
            </div>
            
            <ExplanationKpiCard 
              title="Durchschn. Verkürzung" 
              value={stats.avg_shortened_days || 0}
              format="days"
              description="Tage der Einsatzverkürzung"
              bgColorClass="bg-amber-50/70 dark:bg-amber-900/70"
              borderColorClass="border-amber-100 dark:border-amber-800"
              textColorClass="text-amber-600 dark:text-amber-400"
              valueColorClass="text-amber-700 dark:text-amber-300"
            />
          </div>
        </div>
      </div>
      
      {/* Outcome: Kundenzufriedenheit */}
      <div className="flex justify-center">
        <div className="w-full">
          <OutcomeKpiCard 
            title="Kundenzufriedenheit bei Problemfällen" 
            value={satisfiedPercentageOfProblematic || 0}
          />
        </div>
      </div>
    </div>
  );
};

export default OverviewWidget; 