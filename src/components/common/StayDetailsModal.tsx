import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Loading from './Loading';

interface StayDetail {
  care_stay_id: string;
  customer_name: string;
  customer_city: string;
  problem_type?: string;
  created_at: string;
  arrival?: string;
  planned_arrival?: string;
  departure?: string;
  cancelled_at?: string;
  ended_at?: string;
  cancellation_reason?: string;
  end_reason?: string;
  stay_duration_days?: number;
  actual_duration_days?: number;
  planned_duration_days?: number;
  reduction_percentage?: number;
  stage?: string;
  days_before_arrival?: number;
}

interface GroupedData {
  month: string;
  count: number;
  stays?: StayDetail[];
  cancellations?: StayDetail[];
  terminations?: StayDetail[];
}

interface StayDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  agencyId: string;
  agencyName: string;
  title: string;
  detailType: 'problematic' | 'cancellations' | 'terminations';
  timePeriod: string;
}

const StayDetailsModal: React.FC<StayDetailsModalProps> = ({
  isOpen,
  onClose,
  agencyId,
  agencyName,
  title,
  detailType,
  timePeriod
}) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedMonths, setExpandedMonths] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (isOpen && agencyId) {
      fetchDetails();
    }
  }, [isOpen, agencyId, detailType, timePeriod]);

  const fetchDetails = async () => {
    setIsLoading(true);
    setError(null);
    try {
      let endpoint = '';
      switch (detailType) {
        case 'problematic':
          endpoint = `/api/problematic_stays/details/${agencyId}?time_period=${timePeriod}`;
          break;
        case 'cancellations':
          endpoint = `/api/quotas/${agencyId}/cancellations-before-arrival/details?time_period=${timePeriod}`;
          break;
        case 'terminations':
          endpoint = `/api/quotas/${agencyId}/early-terminations/details?time_period=${timePeriod}`;
          break;
      }
      
      const response = await axios.get(endpoint);
      setData(response.data);
      
      // Auto-expand first month
      if (response.data?.grouped_by_month?.length > 0) {
        setExpandedMonths(new Set([response.data.grouped_by_month[0].month]));
      }
    } catch (err) {
      setError('Fehler beim Laden der Details');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMonth = (month: string) => {
    const newExpanded = new Set(expandedMonths);
    if (newExpanded.has(month)) {
      newExpanded.delete(month);
    } else {
      newExpanded.add(month);
    }
    setExpandedMonths(newExpanded);
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('de-DE');
  };

  const formatMonthName = (monthKey: string) => {
    const [year, month] = monthKey.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('de-DE', { month: 'long', year: 'numeric' });
  };

  const getStaysFromGroup = (group: GroupedData) => {
    return group.stays || group.cancellations || group.terminations || [];
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
              {agencyName} - {title}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
              {data?.total_count || 0} Einsätze betroffen
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading ? (
            <Loading message="Details werden geladen..." />
          ) : error ? (
            <div className="text-red-600 text-center py-8">{error}</div>
          ) : data?.grouped_by_month?.length === 0 ? (
            <div className="text-gray-500 text-center py-8">Keine Daten verfügbar</div>
          ) : (
            <div className="space-y-4">
              {data?.grouped_by_month?.map((group: GroupedData) => (
                <div key={group.month} className="border border-gray-200 dark:border-gray-700 rounded-lg">
                  <button
                    onClick={() => toggleMonth(group.month)}
                    className="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <svg
                        className={`w-5 h-5 text-gray-500 transform transition-transform ${
                          expandedMonths.has(group.month) ? 'rotate-90' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      <span className="font-medium text-gray-800 dark:text-white">
                        {formatMonthName(group.month)}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-300">
                      {group.count} {group.count === 1 ? 'Einsatz' : 'Einsätze'}
                    </span>
                  </button>

                  {expandedMonths.has(group.month) && (
                    <div className="px-4 py-3 space-y-3 border-t border-gray-200 dark:border-gray-700">
                      {getStaysFromGroup(group).map((stay: StayDetail, index: number) => (
                        <div
                          key={`${stay.care_stay_id}-${index}-${stay.customer_name}`}
                          className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="font-medium text-gray-800 dark:text-white">
                                {stay.customer_name} ({stay.customer_city})
                              </div>
                              
                              {detailType === 'problematic' && (
                                <>
                                  <div className="text-gray-600 dark:text-gray-300 mt-1">
                                    Problem: {stay.problem_type}
                                  </div>
                                  {stay.cancellation_reason && (
                                    <div className="text-gray-600 dark:text-gray-300">
                                      Grund: {stay.cancellation_reason}
                                    </div>
                                  )}
                                  {stay.end_reason && (
                                    <div className="text-gray-600 dark:text-gray-300">
                                      Grund: {stay.end_reason}
                                    </div>
                                  )}
                                </>
                              )}

                              {detailType === 'cancellations' && (
                                <>
                                  <div className="text-gray-600 dark:text-gray-300 mt-1">
                                    Geplante Anreise: {formatDate(stay.planned_arrival)}
                                  </div>
                                  <div className="text-gray-600 dark:text-gray-300">
                                    Abgebrochen am: {formatDate(stay.cancelled_at)} 
                                    {stay.days_before_arrival && ` (${stay.days_before_arrival} Tage vorher)`}
                                  </div>
                                  {stay.cancellation_reason && (
                                    <div className="text-gray-600 dark:text-gray-300">
                                      Grund: {stay.cancellation_reason}
                                    </div>
                                  )}
                                </>
                              )}

                              {detailType === 'terminations' && (
                                <>
                                  <div className="text-gray-600 dark:text-gray-300 mt-1">
                                    Anreise: {formatDate(stay.arrival)} - Abreise: {formatDate(stay.departure)}
                                  </div>
                                  <div className="text-gray-600 dark:text-gray-300">
                                    Dauer: {stay.actual_duration_days} Tage 
                                    (geplant: {stay.planned_duration_days} Tage)
                                  </div>
                                  <div className="text-gray-600 dark:text-gray-300">
                                    Verkürzung: {stay.reduction_percentage}%
                                  </div>
                                  {stay.end_reason && (
                                    <div className="text-gray-600 dark:text-gray-300">
                                      Grund: {stay.end_reason}
                                    </div>
                                  )}
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StayDetailsModal;