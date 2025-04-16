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

export interface KPIData {
  agency_id: string;
  agency_name?: string;
  total_jobs_viewed?: number;
  total_jobs_reserved?: number;
  total_jobs_fulfilled?: number;
  total_jobs_cancelled?: number;
  total_jobs_pending?: number;
  total_caregivers_assigned?: number;
  total_caregivers_started?: number;
  total_ended_early?: number;
  total_completed?: number;
  reservation_rate?: number;
  fulfillment_rate?: number;
  cancellation_rate?: number;
  start_rate?: number;
  completion_rate?: number;
  early_end_rate?: number;
}

export interface ResponseTimeData {
  agency_id: string;
  agency_name?: string;
  avg_time_to_reservation?: number;
  avg_time_to_proposal?: number;
  avg_time_to_cancellation?: number;
  avg_time_before_start?: number;
  avg_time_to_any_cancellation?: number;
}

export interface ProfileQualityData {
  agency_id: string;
  agency_name?: string;
  total_caregivers?: number;
  experience_violations?: number;
  language_violations?: number;
  smoker_violations?: number;
  age_violations?: number;
  license_violations?: number;
  experience_violation_rate?: number;
  language_violation_rate?: number;
  smoker_violation_rate?: number;
  age_violation_rate?: number;
  license_violation_rate?: number;
}

export interface StrengthWeaknessItem {
  metric_key: string;
  metric_name: string;
  value: number;
  value_formatted: string;
  benchmark: number;
  benchmark_formatted: string;
  difference: number;
  category: 'strength' | 'weakness' | 'neutral';
  category_name: string;
  normalized_score: number;
}

export interface StrengthWeaknessAnalysis {
  agency_id: string;
  agency_name?: string;
  strengths: StrengthWeaknessItem[];
  weaknesses: StrengthWeaknessItem[];
  neutral: StrengthWeaknessItem[];
  overall_score: number;
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
    const response = await api.get('/agencies');
    return response.data;
  },

  getAgency: async (id: string): Promise<Agency> => {
    const response = await api.get(`/agencies/${id}`);
    return response.data;
  },

  // KPIs
  getAgencyKPIs: async (id: string, timePeriod: string): Promise<KPIData> => {
    const response = await api.get(`/kpis/${id}?time_period=${timePeriod}`);
    return response.data;
  },

  compareAgencyKPIs: async (id: string, timePeriod: string): Promise<ComparisonData> => {
    const response = await api.post('/kpis/compare', { agency_id: id, time_period: timePeriod });
    return response.data;
  },

  // Response Times
  getAgencyResponseTimes: async (id: string, timePeriod: string): Promise<ResponseTimeData> => {
    const response = await api.get(`/response-times/${id}?time_period=${timePeriod}`);
    return response.data;
  },

  compareAgencyResponseTimes: async (id: string, timePeriod: string): Promise<ComparisonData> => {
    const response = await api.post('/response-times/compare', { agency_id: id, time_period: timePeriod });
    return response.data;
  },

  // Profile Quality
  getAgencyProfileQuality: async (id: string, timePeriod: string): Promise<ProfileQualityData> => {
    const response = await api.get(`/profile-quality/${id}?time_period=${timePeriod}`);
    return response.data;
  },

  compareAgencyProfileQuality: async (id: string, timePeriod: string): Promise<ComparisonData> => {
    const response = await api.post('/profile-quality/compare', { agency_id: id, time_period: timePeriod });
    return response.data;
  },

  // LLM Analysis
  getStrengthWeaknessAnalysis: async (id: string, timePeriod: string): Promise<StrengthWeaknessAnalysis> => {
    const response = await api.get(`/llm-analysis/${id}/strength-weakness?time_period=${timePeriod}`);
    return response.data;
  },

  getCancellationAnalysis: async (id: string, timePeriod: string): Promise<any> => {
    const response = await api.get(`/llm-analysis/${id}/cancellations?time_period=${timePeriod}`);
    return response.data;
  },

  getViolationsAnalysis: async (id: string, timePeriod: string): Promise<any> => {
    const response = await api.get(`/llm-analysis/${id}/violations?time_period=${timePeriod}`);
    return response.data;
  },
  
  getAgencySummary: async (id: string, timePeriod: string): Promise<any> => {
    const response = await api.get(`/llm-analysis/${id}/summary?time_period=${timePeriod}`);
    return response.data;
  }
};

export default apiService; 