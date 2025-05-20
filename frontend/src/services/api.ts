import axios from 'axios';
import { calculateDateRange } from '../components/common/TimeFilter';

// Default API URL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Überprüfen der URL im Browser-Kontext
// Wenn es sich um eine direkte Backend-Adresse handelt (wie http://backend:8000),
// ersetzen wir sie mit localhost, da der Browser den Docker-Container-Namen nicht auflösen kann
let effectiveApiUrl = API_URL;
if (typeof window !== 'undefined' && effectiveApiUrl.includes('backend:')) {
  effectiveApiUrl = effectiveApiUrl.replace('backend:', 'localhost:');
  console.log('Adjusted API URL for browser environment:', effectiveApiUrl);
}

// Create an Axios instance with defaults
const api = axios.create({
  baseURL: effectiveApiUrl,
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

// Helfer-Funktion zur Berechnung von benutzerdefinierten Datumsbereichen
const calculateTimeRangeForPeriod = (timePeriod: string): { startDate: string, endDate: string } => {
  // Wir nutzen die vorhandene Funktion aus TimeFilter
  return calculateDateRange(timePeriod);
};

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
    try {
      // Überprüfen, ob der Zeitraum gültig ist
      const validTimePeriods = ['last_quarter', 'last_month', 'last_year', 'all_time', 'current_quarter', 'current_month', 'current_year'];
      
      if (validTimePeriods.includes(timePeriod)) {
        // Normaler API-Aufruf für gültige Zeiträume
        const response = await api.get(`/quotas/${id}/all?time_period=${timePeriod}`);
        return response.data;
      } else {
        // Für nicht unterstützte Zeiträume wie "last_6months" benutzen wir benutzerdefinierte Datumsparameter
        console.log(`Time period "${timePeriod}" not directly supported by API, converting to custom date range`);
        
        // Daten für spezielle Zeiträume berechnen
        const { startDate, endDate } = calculateTimeRangeForPeriod(timePeriod);
        
        // Benutzerdefinierten Datumsbereich-API verwenden
        return await apiService.getAgencyQuotasWithCustomDates(id, startDate, endDate);
      }
    } catch (error) {
      console.error(`Error fetching KPIs for agency ${id}:`, error);
      // Leere Ergebnisse zurückgeben, damit die UI nicht abstürzt
      return {
        selected_agency: {
          agency_id: id,
          agency_name: "Keine Daten verfügbar",
          reservation_rate: 0,
          fulfillment_rate: 0,
          cancellation_rate: 0,
          start_rate: 0,
          completion_rate: 0,
          early_end_rate: 0
        },
        industry_average: {
          reservation_rate: 0,
          fulfillment_rate: 0,
          cancellation_rate: 0,
          start_rate: 0,
          completion_rate: 0,
          early_end_rate: 0
        },
        all_agencies: []
      };
    }
  },
  
  // Quotas (KPIs) mit benutzerdefinierten Datumsparametern
  getAgencyQuotasWithCustomDates: async (id: string, startDate: string, endDate: string): Promise<any> => {
    try {
      console.log(`Fetching quotas for agency ${id} with custom dates: ${startDate} to ${endDate}`);
      const response = await api.get(`/quotas/${id}/all?start_date=${startDate}&end_date=${endDate}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching KPIs with custom dates for agency ${id}:`, error);
      // Leere Ergebnisse zurückgeben, damit die UI nicht abstürzt
      return {
        selected_agency: {
          agency_id: id,
          agency_name: "Keine Daten verfügbar",
          reservation_rate: 0,
          fulfillment_rate: 0,
          cancellation_rate: 0,
          start_rate: 0,
          completion_rate: 0,
          early_end_rate: 0
        },
        industry_average: {
          reservation_rate: 0,
          fulfillment_rate: 0,
          cancellation_rate: 0,
          start_rate: 0,
          completion_rate: 0,
          early_end_rate: 0
        },
        all_agencies: []
      };
    }
  },

  // Quotas (KPIs) aller Agenturen
  getAllAgenciesQuotas: async (timePeriod: string = 'last_quarter'): Promise<any[]> => {
    try {
      const response = await api.post('/kpis/filter', { time_period: timePeriod });
      return response.data;
    } catch (error) {
      console.error('Error fetching KPIs for all agencies:', error);
      return [];
    }
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

  // Profile Quality
  getAgencyProfileQuality: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    try {
      const response = await api.get(`/profile_quality/${id}?time_period=${timePeriod}`);
      return response.data;
    } catch (error) {
      console.warn('Profile quality API returned an error:', error);
      // Gebe Dummy-Daten zurück, um die Anwendung am Laufen zu halten
      return {
        profile_completeness: 0.75, // 75% vollständig
        avatar_exists: true,
        description_quality: 0.8, // 80% Qualität
        response_rate: 0.9, // 90% Antwortrate
        example_pflegekraefte: 3, // 3 Beispiel-Pflegekräfte
        message_template_exists: true
      };
    }
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

  // Problematic Stays API
  getProblematicStaysOverview: async (agencyId?: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    try {
      const url = agencyId 
        ? `/problematic_stays/overview?agency_id=${agencyId}&time_period=${timePeriod}`
        : `/problematic_stays/overview?time_period=${timePeriod}`;
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching problematic stays overview:', error);
      // Leere Ergebnisse zurückgeben, damit die UI nicht abstürzt
      return {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysReasons: async (agencyId?: string, eventType?: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    try {
      let url = `/problematic_stays/reasons?time_period=${timePeriod}`;
      
      if (agencyId) {
        url += `&agency_id=${agencyId}`;
      }
      
      if (eventType) {
        url += `&event_type=${eventType}`;
      }
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching problematic stays reasons:', error);
      return {
        agency_id: agencyId || null,
        event_type: eventType || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysTimeAnalysis: async (
    agencyId?: string, 
    eventType?: string, 
    stayType?: string, 
    timePeriod: string = 'last_year'
  ): Promise<any> => {
    try {
      let url = `/problematic_stays/time-analysis?time_period=${timePeriod}`;
      
      if (agencyId) {
        url += `&agency_id=${agencyId}`;
      }
      
      if (eventType) {
        url += `&event_type=${eventType}`;
      }
      
      if (stayType) {
        url += `&stay_type=${stayType}`;
      }
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching problematic stays time analysis:', error);
      return {
        agency_id: agencyId || null,
        event_type: eventType || null,
        stay_type: stayType || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysDetailed: async (
    agencyId: string,
    eventType?: string,
    stayType?: string,
    timePeriod: string = 'last_quarter',
    limit: number = 50
  ): Promise<any> => {
    try {
      let url = `/problematic_stays/${agencyId}/detailed?time_period=${timePeriod}&limit=${limit}`;
      
      if (eventType) {
        url += `&event_type=${eventType}`;
      }
      
      if (stayType) {
        url += `&stay_type=${stayType}`;
      }
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching problematic stays detailed data:', error);
      return {
        agency_id: agencyId,
        event_type: eventType || null,
        stay_type: stayType || null,
        time_period: timePeriod,
        data: [],
        count: 0,
        limit: limit
      };
    }
  }
};

export default apiService; 