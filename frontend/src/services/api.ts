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
}

export interface ComparisonData {
  selected_agency: any;
  all_agencies: any[];
  industry_average: any;
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

  // Comparison (Simplified Average - potentially deprecate or refine later)
  compareAgencyReactionTimes: async (id: string, timePeriod: string = 'last_quarter'): Promise<ComparisonData> => {
    const response = await api.post('/reaction_times/compare', { agency_id: id, time_period: timePeriod });
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
};

export default apiService; 