import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import apiService from '../services/api';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';
import ExportButton from '../components/common/ExportButton';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
} from 'recharts';
import ComparisonScale from '../components/common/ComparisonScale';

interface TopAgency {
  agency_id: string;
  agency_name: string;
  value: number;
}

// Interface für die gebucketen Abbruchdaten
interface CancellationBucketData {
  lt_3_days: { count: number; ratio: string };
  btw_3_7_days: { count: number; ratio: string };
  btw_8_14_days: { count: number; ratio: string };
  btw_15_30_days: { count: number; ratio: string };
  total: number;
}

const ResponseTimesPage: React.FC = () => {
  const { selectedAgency, timePeriod } = useAppStore();
  
  // State für individuelle Daten
  const [postingResStats, setPostingResStats] = useState<any>(null);
  const [resPropStats, setResPropStats] = useState<any>(null);
  const [propCancelStats, setPropCancelStats] = useState<any>(null);
  const [arrivalCancelStats, setArrivalCancelStats] = useState<any>(null);
  
  // State für Durchschnittsdaten
  const [avgPostingResStats, setAvgPostingResStats] = useState<any>(null);
  const [avgResPropStats, setAvgResPropStats] = useState<any>(null);
  const [avgPropCancelStats, setAvgPropCancelStats] = useState<any>(null);
  const [avgArrivalCancelStats, setAvgArrivalCancelStats] = useState<any>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedAgency) {
         // Nur Durchschnitt laden, wenn keine Agentur gewählt ist?
         try {
             setIsLoading(true);
             setError(null);
             const [
                 avgPostingRes,
                 avgResProp,
                 avgPropCancel,
                 avgArrivalCancel
             ] = await Promise.all([
                 apiService.getOverallPostingToReservationStats(timePeriod),
                 apiService.getOverallReservationToFirstProposalStats(timePeriod),
                 apiService.getOverallProposalToCancellationStats(timePeriod),
                 apiService.getOverallArrivalToCancellationStats(timePeriod)
             ]);
             setAvgPostingResStats(avgPostingRes);
             setAvgResPropStats(avgResProp);
             setAvgPropCancelStats(avgPropCancel);
             setAvgArrivalCancelStats(avgArrivalCancel);
         } catch (err) {
             console.error('Error fetching overall reaction times data:', err);
             setError('Fehler beim Laden der Durchschnitts-Reaktionszeiten.');
         } finally {
             setIsLoading(false);
         }
         return;
      }
      
      // Individuelle UND Durchschnittsdaten laden
      try {
        setIsLoading(true);
        setError(null);
        
        const [ 
          postingRes,
          resProp,
          propCancel,
          arrivalCancel,
          avgPostingRes,
          avgResProp,
          avgPropCancel,
          avgArrivalCancel
        ] = await Promise.all([
          // Individuelle Daten
          apiService.getPostingToReservationStats(selectedAgency.agency_id, timePeriod),
          apiService.getReservationToFirstProposalStats(selectedAgency.agency_id, timePeriod),
          apiService.getProposalToCancellationStats(selectedAgency.agency_id, timePeriod),
          apiService.getArrivalToCancellationStats(selectedAgency.agency_id, timePeriod),
          // Durchschnittsdaten
          apiService.getOverallPostingToReservationStats(timePeriod),
          apiService.getOverallReservationToFirstProposalStats(timePeriod),
          apiService.getOverallProposalToCancellationStats(timePeriod),
          apiService.getOverallArrivalToCancellationStats(timePeriod)
        ]);
        
        setPostingResStats(postingRes);
        setResPropStats(resProp);
        setPropCancelStats(propCancel);
        setArrivalCancelStats(arrivalCancel);
        setAvgPostingResStats(avgPostingRes);
        setAvgResPropStats(avgResProp);
        setAvgPropCancelStats(avgPropCancel);
        setAvgArrivalCancelStats(avgArrivalCancel);

      } catch (err) {
        console.error('Error fetching response times data:', err);
        setError('Fehler beim Laden der Reaktionszeiten-Daten.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [selectedAgency, timePeriod]);

  const formatHours = (value: string | number | null | undefined) => {
    if (value === null || value === undefined) return 'N/A';
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(numValue)) return 'N/A';

    if (numValue >= 24) {
      return `${(numValue / 24).toFixed(1)} Tage`;
    }
    return `${numValue.toFixed(1)} Std.`;
  };
  
  const industryAverage = avgResPropStats?.industry_average || {};
  
  // Daten für Abbruch-Bucket-Chart aufbereiten
  const getCancellationChartData = () => {
    if (!arrivalCancelStats?.overall) return [];
    const overall = arrivalCancelStats.overall;
    const total = overall.abgebrochen_vor_arrival || 1; // Vermeide Division durch Null
    
    return [
      { name: '< 3 Tage', value: (overall.lt_3_days?.count / total) * 100 || 0, count: overall.lt_3_days?.count || 0 },
      { name: '3-7 Tage', value: (overall.btw_3_7_days?.count / total) * 100 || 0, count: overall.btw_3_7_days?.count || 0 },
      { name: '8-14 Tage', value: (overall.btw_8_14_days?.count / total) * 100 || 0, count: overall.btw_8_14_days?.count || 0 },
      { name: '15-30 Tage', value: (overall.btw_15_30_days?.count / total) * 100 || 0, count: overall.btw_15_30_days?.count || 0 }
    ];
  };

  if (isLoading) {
    return <Loading message="Reaktionszeiten-Daten werden geladen..." />;
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
    <div className="response-times-page">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Reaktionszeiten: {selectedAgency.agency_name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Detaillierte Analyse der Reaktionszeiten und Abbruch-Timings
          </p>
        </div>
        <ExportButton 
          targetElementId="response-times-content" 
          filename="reaktionszeiten-analyse" 
          pageTitle="Reaktionszeiten-Analyse" 
        />
      </div>

      <div id="response-times-content" className="print-container">
        {/* Abschnitt 1: Kern-Reaktionszeiten mit ComparisonScale */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Kern-Reaktionszeiten (Median)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <ComparisonScale 
              label="Posting → Reservierung"
              agencyName={selectedAgency?.agency_name}
              agencyValue={postingResStats?.median_hours}
              averageValue={avgPostingResStats?.median_hours} 
              formatValue={formatHours}
              evaluationType='neutral'
              tooltip="Medianzeit von Veröffentlichung der Stelle bis zur Reservierung durch die Agentur."
            />
            <ComparisonScale 
              label="Reservierung → Erster Vorschlag"
              agencyName={selectedAgency?.agency_name}
              agencyValue={resPropStats?.median_hours}
              averageValue={avgResPropStats?.median_hours}
              formatValue={formatHours}
              evaluationType='neutral'
              tooltip="Medianzeit von Reservierung bis zum ersten Personalvorschlag (CareStay)."
            />
            <ComparisonScale 
              label="Vorschlag → Abbruch (vor Anreise)"
              agencyName={selectedAgency?.agency_name}
              agencyValue={propCancelStats?.median_hours}
              averageValue={avgPropCancelStats?.median_hours}
              formatValue={formatHours}
              evaluationType='neutral'
              tooltip="Medianzeit von Personalvorschlag bis zum Abbruch durch die Agentur (vor geplanter Anreise)."
            />
            <ComparisonScale 
              label="Abbruch vor Anreise (Ersteinsatz)"
              agencyName={selectedAgency?.agency_name}
              agencyValue={arrivalCancelStats?.first_stays?.median_hours}
              averageValue={avgArrivalCancelStats?.first_stays?.median_hours}
              formatValue={formatHours}
              evaluationType='lowerIsBetter'
              tooltip="Medianzeit zwischen geplantem Anreisedatum und Abbruch (nur Ersteinsätze). Niedriger ist schlechter."
            />
          </div>
        </section>

        {/* Abschnitt 2: Abbruch-Timing (vor Anreise) */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Abbruch-Timing (vor Anreise)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold mb-2">Verteilung der Abbruch-Zeitpunkte</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Prozentuale Verteilung, wie viele Tage vor geplanter Anreise die Agentur einen Einsatz abbricht. 
                (Basierend auf {arrivalCancelStats?.overall?.abgebrochen_vor_arrival || 0} Fällen)
              </p>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={getCancellationChartData()} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" unit="%" domain={[0, 100]}/>
                    <YAxis type="category" dataKey="name" width={80}/>
                    <Tooltip formatter={(value: number, name, props) => [`${value.toFixed(1)}% (${props.payload.count} Fälle)`, "Anteil"]}/>
                    <Bar dataKey="value" fill="#ef4444" name="Anteil" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold mb-2">Abbruch-Details</h3>
              <table className="data-table w-full">
                <thead>
                  <tr><th>Zeitraum vor Anreise</th><th>Anzahl</th><th>Anteil</th></tr>
                </thead>
                <tbody>
                  <tr><td>&lt; 3 Tage</td><td>{arrivalCancelStats?.overall?.lt_3_days?.count || 0}</td><td>{arrivalCancelStats?.overall?.lt_3_days?.ratio || '0.0%'}</td></tr>
                  <tr><td>3-7 Tage</td><td>{arrivalCancelStats?.overall?.btw_3_7_days?.count || 0}</td><td>{arrivalCancelStats?.overall?.btw_3_7_days?.ratio || '0.0%'}</td></tr>
                  <tr><td>8-14 Tage</td><td>{arrivalCancelStats?.overall?.btw_8_14_days?.count || 0}</td><td>{arrivalCancelStats?.overall?.btw_8_14_days?.ratio || '0.0%'}</td></tr>
                  <tr><td>15-30 Tage</td><td>{arrivalCancelStats?.overall?.btw_15_30_days?.count || 0}</td><td>{arrivalCancelStats?.overall?.btw_15_30_days?.ratio || '0.0%'}</td></tr>
                  <tr><td>**Gesamt**</td><td>**{arrivalCancelStats?.overall?.abgebrochen_vor_arrival || 0}**</td><td>**100.0%**</td></tr>
                </tbody>
              </table>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Hinweis: Der Durchschnittsvergleich ist für die Bucket-Verteilung noch nicht verfügbar.
              </p>
            </div>
          </div>
        </section>

        {/* Abschnitt 3: Detaillierte Statistiken */}
        <section>
           <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Detaillierte Statistiken (Median / Durchschnitt)</h2>
           <div className="overflow-x-auto">
             <table className="data-table w-full">
                <thead>
                  <tr>
                    <th>Metrik</th>
                    <th>Agentur (Median)</th><th>Agentur (Schnitt)</th>
                    <th>Durchschnitt (Median)</th><th>Durchschnitt (Schnitt)</th>
                 </tr>
                </thead>
                 <tbody>
                  <tr><td>Posting → Reservierung</td><td>{formatHours(postingResStats?.median_hours)}</td><td>{formatHours(postingResStats?.avg_hours)}</td><td>{formatHours(avgPostingResStats?.median_hours)}</td><td>{formatHours(avgPostingResStats?.avg_hours)}</td></tr>
                  <tr><td>Reservierung → Erster Vorschlag</td><td>{formatHours(resPropStats?.median_hours)}</td><td>{formatHours(resPropStats?.avg_hours)}</td><td>{formatHours(avgResPropStats?.median_hours)}</td><td>{formatHours(avgResPropStats?.avg_hours)}</td></tr>
                  <tr><td>Vorschlag → Abbruch (vor Anreise)</td><td>{formatHours(propCancelStats?.median_hours)}</td><td>{formatHours(propCancelStats?.avg_hours)}</td><td>{formatHours(avgPropCancelStats?.median_hours)}</td><td>{formatHours(avgPropCancelStats?.avg_hours)}</td></tr>
                  <tr><td>Abbruch vor Anreise (Gesamt)</td><td>{formatHours(arrivalCancelStats?.overall?.median_hours)}</td><td>{formatHours(arrivalCancelStats?.overall?.avg_hours)}</td><td>{formatHours(avgArrivalCancelStats?.overall?.median_hours)}</td><td>{formatHours(avgArrivalCancelStats?.overall?.avg_hours)}</td></tr>
                  <tr><td>Abbruch vor Anreise (Ersteinsatz)</td><td>{formatHours(arrivalCancelStats?.first_stays?.median_hours)}</td><td>{formatHours(arrivalCancelStats?.first_stays?.avg_hours)}</td><td>{formatHours(avgArrivalCancelStats?.first_stays?.median_hours)}</td><td>{formatHours(avgArrivalCancelStats?.first_stays?.avg_hours)}</td></tr>
                  <tr><td>Abbruch vor Anreise (Folgeeinsatz)</td><td>{formatHours(arrivalCancelStats?.followup_stays?.median_hours)}</td><td>{formatHours(arrivalCancelStats?.followup_stays?.avg_hours)}</td><td>{formatHours(avgArrivalCancelStats?.followup_stays?.median_hours)}</td><td>{formatHours(avgArrivalCancelStats?.followup_stays?.avg_hours)}</td></tr>
                 </tbody>
             </table>
           </div>
        </section>
      </div>
    </div>
  );
};

export default ResponseTimesPage; 