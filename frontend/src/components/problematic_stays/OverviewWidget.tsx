import React from 'react';

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
  // Wenn noch keine Daten geladen sind oder das Datenformat nicht stimmt
  if (isLoading || !data || data.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 h-32"></div>
        ))}
      </div>
    );
  }

  // Daten aus dem ersten Element extrahieren (wir erwarten nur ein Element im Array)
  const stats = data[0];

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
      <div className="flex items-center mt-1 text-sm">
        <span className="text-gray-500 dark:text-gray-400">vs. Durchschnitt: </span>
        <span className={`font-medium ml-1 ${difference > 0 ? 'text-red-500' : difference < 0 ? 'text-green-500' : 'text-gray-500'}`}>
          {comparisonValue !== 0 ? `${Math.abs(percentageDifference).toFixed(1)}%` : 'N/A'}
        </span>
        <TrendIndicator value={difference} />
      </div>
    );
  };

  // KPI-Karte-Komponente
  const KpiCard = ({ 
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</h3>
        <div className="mt-2 flex items-baseline">
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            {formattedValue}
          </span>
        </div>
        {description && (
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{description}</p>
        )}
        {comparisonValue !== undefined && <ComparisonValue value={value} comparisonValue={comparisonValue} />}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Gesamtanteil problematischer Einsätze */}
      <KpiCard 
        title="Problematische Einsätze" 
        value={stats.problematic_percentage || 0}
        comparisonValue={0} // Hier den Vergleichswert einfügen
        description="Anteil an allen Pflegeeinsätzen"
      />
      
      {/* Abbrüche vor Anreise */}
      <KpiCard 
        title="Abbrüche vor Anreise" 
        value={stats.cancelled_percentage || 0}
        comparisonValue={0} // Hier den Vergleichswert einfügen
        description={`${stats.cancelled_before_arrival_count || 0} Einsätze`}
      />
      
      {/* Vorzeitige Beendigungen */}
      <KpiCard 
        title="Vorzeitige Beendigungen" 
        value={stats.shortened_percentage || 0}
        comparisonValue={0} // Hier den Vergleichswert einfügen
        description={`${stats.shortened_after_arrival_count || 0} Einsätze`}
      />
      
      {/* Sofortige Abreisen */}
      <KpiCard 
        title="Sofortige Abreisen (<10 Tage)" 
        value={stats.instant_departure_percentage || 0}
        comparisonValue={0} // Hier den Vergleichswert einfügen
        description={`${stats.instant_departure_count || 0} Einsätze`}
      />
      
      {/* Vorlaufzeit bei Abbrüchen */}
      <KpiCard 
        title="Vorlaufzeit bei Abbrüchen" 
        value={stats.avg_days_before_arrival || 0}
        format="days"
        description="Durchschnittliche Tage vor Anreise"
      />
      
      {/* Verkürzungstage */}
      <KpiCard 
        title="Durchschn. Verkürzung" 
        value={stats.avg_shortened_days || 0}
        format="days"
        description="Tage der Einsatzverkürzung"
      />
      
      {/* Ersatzbereitstellung */}
      <KpiCard 
        title="Ersatzbereitstellung" 
        value={stats.replacement_percentage || 0}
        description={`Bei ${stats.with_replacement_count || 0} Abbrüchen`}
      />
      
      {/* Kundenzufriedenheit */}
      <KpiCard 
        title="Kundenzufriedenheit" 
        value={stats.satisfied_percentage || 0}
        description={`${stats.satisfied_count || 0} zufriedene Kunden`}
      />
    </div>
  );
};

export default OverviewWidget; 