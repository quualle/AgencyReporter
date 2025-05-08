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
  const [cancellationRateData, setCancellationRateData] = useState<any>(null);
  
  // State für Durchschnittsdaten
  const [avgPostingResStats, setAvgPostingResStats] = useState<any>(null);
  const [avgResPropStats, setAvgResPropStats] = useState<any>(null);
  const [avgPropCancelStats, setAvgPropCancelStats] = useState<any>(null);
  const [avgArrivalCancelStats, setAvgArrivalCancelStats] = useState<any>(null);
  const [avgCancellationStats, setAvgCancellationStats] = useState<any>(null);

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
          cancellationRate,
          avgPostingRes,
          avgResProp,
          avgPropCancel,
          avgArrivalCancel,
          avgCancellationRate
        ] = await Promise.all([
          // Individuelle Daten
          apiService.getPostingToReservationStats(selectedAgency.agency_id, timePeriod),
          apiService.getReservationToFirstProposalStats(selectedAgency.agency_id, timePeriod),
          apiService.getProposalToCancellationStats(selectedAgency.agency_id, timePeriod),
          apiService.getArrivalToCancellationStats(selectedAgency.agency_id, timePeriod),
          apiService.getCancellationBeforeArrivalRate(selectedAgency.agency_id, timePeriod),
          // Durchschnittsdaten
          apiService.getOverallPostingToReservationStats(timePeriod),
          apiService.getOverallReservationToFirstProposalStats(timePeriod),
          apiService.getOverallProposalToCancellationStats(timePeriod),
          apiService.getOverallArrivalToCancellationStats(timePeriod),
          apiService.getOverallCancellationBeforeArrivalStats(timePeriod)
        ]);
        
        setPostingResStats(postingRes);
        setResPropStats(resProp);
        setPropCancelStats(propCancel);
        setArrivalCancelStats(arrivalCancel);
        setCancellationRateData(cancellationRate);
        setAvgPostingResStats(avgPostingRes);
        setAvgResPropStats(avgResProp);
        setAvgPropCancelStats(avgPropCancel);
        setAvgArrivalCancelStats(avgArrivalCancel);
        setAvgCancellationStats(avgCancellationRate);

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
  
  // Prepare data for the cancellation bucket chart
  const getCancellationBucketChartData = (): { name: string; count: number; ratio: string; color: string; percentage: number; label: string; avgPercentage?: number }[] => {
    const buckets = cancellationRateData?.cancellation_buckets?.gesamt;
    const avgBuckets = avgCancellationStats?.avg_cancellation_buckets;
    const proposal_count = cancellationRateData?.proposal_count || 1;
    const avg_proposal_count = avgCancellationStats?.avg_proposal_count || 1;

    console.log("----- Calculating Chart Data -----");
    console.log("Raw AvgCancellationStats in getCancellationBucketChartData:", avgCancellationStats);
    console.log("Avg Buckets (gesamt):", avgBuckets);
    console.log("Avg Proposal Count:", avg_proposal_count);
    
    if (!buckets || proposal_count === 0) return [];

    const data = [
      { name: '< 3 Tage', count: buckets.lt_3_days?.count ?? 0, ratio: buckets.lt_3_days?.ratio ?? '0.0%', color: '#ef4444', avgCount: avgBuckets?.lt_3_days?.count },
      { name: '3-7 Tage', count: buckets.btw_3_7_days?.count ?? 0, ratio: buckets.btw_3_7_days?.ratio ?? '0.0%', color: '#f97316', avgCount: avgBuckets?.btw_3_7_days?.count },
      { name: '8-14 Tage', count: buckets.btw_8_14_days?.count ?? 0, ratio: buckets.btw_8_14_days?.ratio ?? '0.0%', color: '#eab308', avgCount: avgBuckets?.btw_8_14_days?.count },
      { name: '15-30 Tage', count: buckets.btw_15_30_days?.count ?? 0, ratio: buckets.btw_15_30_days?.ratio ?? '0.0%', color: '#22c55e', avgCount: avgBuckets?.btw_15_30_days?.count }
    ];
    
     const resultData = data.map(item => {
       const calculatedAvgPercentage = avg_proposal_count > 0 ? ((item.avgCount || 0) / avg_proposal_count) * 100 : 0;
       console.log(`Item: ${item.name}, AvgCount: ${item.avgCount}, AvgProposalCount: ${avg_proposal_count}, CalculatedAvgPercentage: ${calculatedAvgPercentage}`);
       return {
           ...item,
           percentage: proposal_count > 0 ? ((item.count || 0) / proposal_count) * 100 : 0,
           avgPercentage: calculatedAvgPercentage,
           label: `${item.count} / ${proposal_count}`
       };
    });
    console.log("Final Chart Data:", resultData);
    return resultData;
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
        {/* Abschnitt 1: Kern-Reaktionszeiten mit ComparisonScale & Details Button */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Kern-Reaktionszeiten (Median)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="dashboard-card border-b-4 border-b-blue-500 relative">
                <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-t-blue-500 border-l-transparent border-r-transparent z-10"></div>
                <ComparisonScale 
                  label="Abbruch vor Anreise (Ersteinsatz)"
                  agencyName={selectedAgency?.agency_name}
                  agencyValue={arrivalCancelStats?.first_stays?.median_hours}
                  averageValue={avgArrivalCancelStats?.first_stays?.median_hours}
                  formatValue={formatHours}
                  evaluationType='higherIsBetter'
                  tooltip="Medianzeit zwischen geplantem Anreisedatum und Abbruch (nur Ersteinsätze). Mehr Zeit im Voraus ist besser."
                />
            </div>
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
          </div>
            
          <div className="mt-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-600 shadow-md border-l-4 border-l-blue-500 lg:ml-4">
              <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">Analyse: Abbruch vor Anreise</h3>
              <div className="flex items-baseline space-x-4 mb-4">
                <div className="text-center">
                    <span className={`text-3xl font-bold ${ (parseFloat(cancellationRateData?.cancellation_ratio_gesamt?.replace('%','') || '0') <= parseFloat(avgCancellationStats?.avg_cancellation_ratio_gesamt?.replace('%','') || '0')) ? 'text-green-500' : 'text-red-500'}`}>
                        {cancellationRateData?.cancellation_ratio_gesamt ?? 'N/A'}
                    </span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Abbruchrate (Gesamt)</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">(Ø {avgCancellationStats?.avg_cancellation_ratio_gesamt ?? 'N/A'})</p>
                </div>
                 <div className="text-center border-l pl-4 border-gray-300 dark:border-gray-600">
                    <span className="text-xl font-semibold text-gray-700 dark:text-gray-300">{cancellationRateData?.cancellation_buckets?.gesamt?.count ?? 0}</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Abbrüche</p>
                     <p className="text-xs text-gray-400 dark:text-gray-500">(Ø {avgCancellationStats?.avg_cancellation_buckets?.gesamt?.count?.toFixed(1) ?? 'N/A'})</p>
                </div>
                 <div className="text-center">
                     <span className="text-xl font-semibold text-gray-700 dark:text-gray-300">{cancellationRateData?.proposal_count ?? 0}</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Vorschläge</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">(Ø {avgCancellationStats?.avg_proposal_count?.toFixed(1) ?? 'N/A'})</p>
                </div>
              </div>
              
              <h4 className="font-medium text-md mb-2 text-gray-700 dark:text-gray-200">Kurzfristigkeit der Abbrüche (Vergleich zum Durchschnitt)</h4>
               <div className="h-48"> 
                  <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getCancellationBucketChartData()} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" unit="%" domain={[0, 100]}/>
                        <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 12 }}/>
                        <Tooltip formatter={(value: number, name: string, props: any) => {
                            if (name === 'Agentur') return [`${value.toFixed(1)}% (${props.payload.count} Fälle)`, name];
                            if (name === 'Durchschnitt') return [`${value.toFixed(1)}%`, name];
                            return [value, name];
                        }}/>
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="avgPercentage" name="Durchschnitt" fill="#cbd5e1" radius={[0, 4, 4, 0]} barSize={10}/>
                        <Bar dataKey="percentage" name="Agentur" label={{ position: 'right', formatter: (entry: any) => entry.label ?? '', fontSize: 10 }} radius={[0, 4, 4, 0]} barSize={10}>
                          {getCancellationBucketChartData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                    </BarChart>
                  </ResponsiveContainer>
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