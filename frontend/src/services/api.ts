import axios from 'axios';

// Default API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create an Axios instance with defaults
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Types
export interface Agency {
  agency_id: string;
  agency_name: string;
  created_at?: string;
  status?: string;
  location?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active_recently?: boolean;
}

export interface ComparisonData {
  selected_agency: any;
  all_agencies: any[];
  industry_average: any;
  comparison_agency?: any; // Für den Vergleich mit einer spezifischen Agentur
  historical_data?: any; // Für den historischen Vergleich
}

// API functions
export const apiService = {
  // Agencies
  getAgencies: async (): Promise<Agency[]> => {
    const response = await api.get('/agencies/');
    return response.data;
  },

  getAgency: async (id: string): Promise<Agency> => {
    const response = await api.get(`/agencies/${id}`);
    return response.data;
  },

  // Quotas (KPIs)
  getAgencyQuotas: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas/${id}/all?time_period=${timePeriod}`);
    return response.data;
  },
  
  // Quotas (KPIs) mit benutzerdefinierten Datumsparametern
  getAgencyQuotasWithCustomDates: async (id: string, startDate: string, endDate: string): Promise<any> => {
    const response = await api.get(`/quotas/${id}/all?start_date=${startDate}&end_date=${endDate}`);
    return response.data;
  },

  getCancellationBeforeArrivalRate: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas/${id}/cancellation-before-arrival?time_period=${timePeriod}`);
    return response.data;
  },

  // Reaction Times - Einzelne Agentur
  getAgencyReactionTimes: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/${id}?time_period=${timePeriod}`);
    return response.data;
  },
  getPostingToReservationStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/${id}/posting_to_reservation?time_period=${timePeriod}`);
    return response.data;
  },
  getReservationToFirstProposalStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/${id}/reservation_to_first_proposal?time_period=${timePeriod}`);
    return response.data;
  },
  getProposalToCancellationStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/${id}/proposal_to_cancellation?time_period=${timePeriod}`);
    return response.data;
  },
  getArrivalToCancellationStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/${id}/arrival_to_cancellation?time_period=${timePeriod}`);
    return response.data;
  },

  // Overall Average Stats (All Agencies)
  getOverallPostingToReservationStats: async (timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/stats/overall/posting_to_reservation?time_period=${timePeriod}`);
    return response.data;
  },
  getOverallReservationToFirstProposalStats: async (timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/stats/overall/reservation_to_first_proposal?time_period=${timePeriod}`);
    return response.data;
  },
  getOverallProposalToCancellationStats: async (timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/stats/overall/proposal_to_cancellation?time_period=${timePeriod}`);
    return response.data;
  },
  getOverallArrivalToCancellationStats: async (timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/reaction_times/stats/overall/arrival_to_cancellation?time_period=${timePeriod}`);
    return response.data;
  },
  getOverallCancellationBeforeArrivalStats: async (timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas/stats/overall/cancellation-before-arrival?time_period=${timePeriod}`);
    return response.data;
  },

  // Comparison (Simplified Average - potentially deprecate or refine later)
  compareAgencyReactionTimes: async (id: string, timePeriod: string = 'last_quarter'): Promise<ComparisonData> => {
    const response = await api.post('/reaction_times/compare', { agency_id: id, time_period: timePeriod });
    return response.data;
  },

  // Neue Vergleichsfunktionen
  compareAgencyWithAgency: async (id: string, compareAgencyId: string, timePeriod: string = 'last_quarter'): Promise<ComparisonData> => {
    const response = await api.post('/quotas/compare', { 
      agency_id: id, 
      compare_agency_id: compareAgencyId, 
      time_period: timePeriod,
      comparison_type: 'agency' 
    });
    return response.data;
  },

  compareAgencyWithHistorical: async (id: string, currentPeriod: string = 'last_quarter', historicalPeriod: string = 'last_year'): Promise<ComparisonData> => {
    const response = await api.post('/quotas/compare', { 
      agency_id: id, 
      current_period: currentPeriod,
      historical_period: historicalPeriod,
      comparison_type: 'historical'
    });
    return response.data;
  },

  getAgencyHistoricalData: async (id: string, periods: string[] = ['last_quarter', 'last_year']): Promise<any> => {
    const response = await api.get(`/quotas/${id}/historical?periods=${periods.join(',')}`);
    return response.data;
  },

  // Profile Quality
  getAgencyProfileQuality: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/profile_quality/${id}?time_period=${timePeriod}`);
    return response.data;
  },

  // Quotas with Reasons
  getAgencyEarlyEndReasons: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas_with_reasons/${id}/early-end-reasons?time_period=${timePeriod}`);
    return response.data;
  },

  getAgencyCancellationReasons: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas_with_reasons/${id}/cancellation-reasons?time_period=${timePeriod}`);
    return response.data;
  },
};

export default apiService; 