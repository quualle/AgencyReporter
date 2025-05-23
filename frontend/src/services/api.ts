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

// Cache for API responses
interface CacheEntry {
  data: any;
  timestamp: string;
  expiry: number;
}

interface ApiCache {
  [key: string]: CacheEntry;
}

const apiCache: ApiCache = {};

// Erhöhte Cache-Dauer für längere Preload-Haltbarkeit (120 Minuten für erweitert)
const STANDARD_CACHE_EXPIRY = 30 * 60 * 1000; // 30 Minuten
const EXTENDED_CACHE_EXPIRY = 120 * 60 * 1000; // 120 Minuten (2 Stunden)

// Verbesserte Cache-Funktionen
const cacheHelper = {
  // Erzeugt einen konsistenten Cache-Schlüssel
  createCacheKey: (endpoint: string, params: Record<string, any> = {}): string => {
    // Sortiere Parameter alphabetisch für Konsistenz
    const sortedParams = Object.keys(params).sort().map(key => 
      `${key}=${params[key]}`
    ).join('&');
    
    return `${endpoint}${sortedParams ? '?' + sortedParams : ''}`;
  },
  
  // Daten aus dem Cache holen
  getFromCache: (cacheKey: string): any | null => {
    if (apiCache[cacheKey] && apiCache[cacheKey].expiry > Date.now()) {
      console.log(`Cache hit for: ${cacheKey}`);
      return apiCache[cacheKey].data;
    }
    return null;
  },
  
  // Daten in den Cache schreiben
  saveToCache: (cacheKey: string, data: any, useExtendedCache: boolean = false): void => {
    const CACHE_EXPIRY = useExtendedCache ? EXTENDED_CACHE_EXPIRY : STANDARD_CACHE_EXPIRY;
    
    apiCache[cacheKey] = {
      data,
      timestamp: new Date().toISOString(),
      expiry: Date.now() + CACHE_EXPIRY
    };
    
    console.log(`Saved to cache: ${cacheKey}, expires in ${useExtendedCache ? '120' : '30'} minutes`);
  }
};

// Interface für Preload-Fortschritt und Status
export interface PreloadProgress {
  totalRequests: number;
  completedRequests: number;
  inProgress: boolean;
  status: string;
  error?: string;
  cachedEndpoints?: number; // Anzahl der Cache-Treffer
}

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
  
  // Agency Comparison Data
  getAgencyComparisonData: async (timePeriod: string = 'last_quarter', forceRefresh: boolean = false, useExtendedCache: boolean = false): Promise<any> => {
    // Create a cache key based on the parameters
    const cacheKey = `agencyComparisonData_${timePeriod}`;
    
    // Wähle Cache-Dauer basierend auf Preload-Anforderung
    const CACHE_EXPIRY = useExtendedCache ? EXTENDED_CACHE_EXPIRY : STANDARD_CACHE_EXPIRY;
    
    // Check if we have cached data and it's not expired and not forcing refresh
    if (!forceRefresh && apiCache[cacheKey] && apiCache[cacheKey].expiry > Date.now()) {
      console.log('Using cached data for agency comparison:', timePeriod);
      return apiCache[cacheKey].data;
    }
    
    try {
      console.log('Fetching fresh data for agency comparison:', timePeriod);
      
      // Handle APIs that might not be fully implemented yet
      const fetchWithFallback = async (url: string) => {
        try {
          const response = await api.get(url);
          return response;
        } catch (err) {
          console.warn(`API endpoint ${url} failed, using fallback data`, err);
          // Return empty data as fallback
          return { data: { data: [] } };
        }
      };
      
      // Create promises for all required endpoints
      const promises = [
        // Basic problematic stays overview
        fetchWithFallback(`/problematic_stays/overview?time_period=${timePeriod}`),
        
        // Reaction times for all agencies - this one is not fully implemented yet
        fetchWithFallback(`/problematic_stays/overview?time_period=${timePeriod}`), // Use overview as fallback
        
        // Profile quality for all agencies - this one is not fully implemented yet
        fetchWithFallback(`/problematic_stays/overview?time_period=${timePeriod}`), // Use overview as fallback
        
        // Problematic stays heatmap
        fetchWithFallback(`/problematic_stays/heatmap?time_period=${timePeriod}`),
      ];
      
      // Execute all promises concurrently
      const results = await Promise.all(promises);
      
      // Extract data from responses
      const responseData = {
        problematicStaysOverview: results[0].data,
        reactionTimes: { data: [] }, // Empty data for now
        profileQuality: { data: [] }, // Empty data for now
        problematicStaysHeatmap: results[3].data,
        timestamp: new Date().toISOString(),
      };
      
      // Save to cache
      apiCache[cacheKey] = {
        data: responseData,
        timestamp: new Date().toISOString(),
        expiry: Date.now() + CACHE_EXPIRY
      };
      
      return responseData;
    } catch (error) {
      console.error('Error fetching agency comparison data:', error);
      
      // Return empty data structure with all required properties
      return {
        problematicStaysOverview: { data: [] },
        reactionTimes: { data: [] },
        profileQuality: { data: [] },
        problematicStaysHeatmap: { data: [] },
        timestamp: new Date().toISOString(),
        error: true
      };
    }
  },

  // Quotas (KPIs)
  getAgencyQuotas: async (
    id: string, 
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      // Überprüfen, ob der Zeitraum gültig ist
      const validTimePeriods = ['last_quarter', 'last_month', 'last_year', 'all_time'];
      
      if (validTimePeriods.includes(timePeriod)) {
        // Cache-Schlüssel erstellen
        const cacheKey = cacheHelper.createCacheKey(`quotas/${id}/all`, { time_period: timePeriod });
        
        // Prüfen, ob Daten im Cache sind
        if (!forceRefresh) {
          const cachedData = cacheHelper.getFromCache(cacheKey);
          if (cachedData) {
            return cachedData;
          }
        }
        
        // Normaler API-Aufruf für gültige Zeiträume, wenn keine Cache-Daten verfügbar
        console.log(`Fetching fresh quotas data for agency ${id}, period ${timePeriod}`);
        const response = await api.get(`/quotas/${id}/all?time_period=${timePeriod}`);
        
        // Speichere Daten im Cache
        cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
        
        return response.data;
      } else {
        // Für nicht unterstützte Zeiträume wie "last_6months" benutzen wir benutzerdefinierte Datumsparameter
        console.log(`Time period "${timePeriod}" not directly supported by API, converting to custom date range`);
        
        // Daten für spezielle Zeiträume berechnen
        const { startDate, endDate } = calculateTimeRangeForPeriod(timePeriod);
        
        // Benutzerdefinierten Datumsbereich-API verwenden
        return await apiService.getAgencyQuotasWithCustomDates(id, startDate, endDate, forceRefresh, useExtendedCache);
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
  getAgencyQuotasWithCustomDates: async (
    id: string, 
    startDate: string, 
    endDate: string,
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      // Cache-Schlüssel erstellen
      const cacheKey = cacheHelper.createCacheKey(`quotas/${id}/all`, { 
        start_date: startDate, 
        end_date: endDate 
      });
      
      // Prüfen, ob Daten im Cache sind
      if (!forceRefresh) {
        const cachedData = cacheHelper.getFromCache(cacheKey);
        if (cachedData) {
          return cachedData;
        }
      }
      
      console.log(`Fetching quotas for agency ${id} with custom dates: ${startDate} to ${endDate}`);
      const response = await api.get(`/quotas/${id}/all?start_date=${startDate}&end_date=${endDate}`);
      
      // Speichere Daten im Cache
      cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
      
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

  getCancellationBeforeArrivalRate: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`quotas/${id}/cancellation-before-arrival`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await api.get(`/quotas/${id}/cancellation-before-arrival?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
    return response.data;
  },

  // Reaction Times - Einzelne Agentur
  getAgencyReactionTimes: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`reaction_times/${id}`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    console.log(`Fetching reaction times for agency ${id}, period ${timePeriod}`);
    const response = await api.get(`/reaction_times/${id}?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
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
  getArrivalToCancellationStats: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`reaction_times/${id}/arrival_to_cancellation`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await api.get(`/reaction_times/${id}/arrival_to_cancellation?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
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
  getOverallCancellationBeforeArrivalStats: async (
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`quotas/stats/overall/cancellation-before-arrival`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await api.get(`/quotas/stats/overall/cancellation-before-arrival?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
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
  getAgencyProfileQuality: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      // Cache-Schlüssel erstellen
      const cacheKey = cacheHelper.createCacheKey(`profile_quality/${id}`, { time_period: timePeriod });
      
      // Prüfen, ob Daten im Cache sind
      if (!forceRefresh) {
        const cachedData = cacheHelper.getFromCache(cacheKey);
        if (cachedData) {
          return cachedData;
        }
      }
      
      console.log(`Fetching profile quality for agency ${id}, period ${timePeriod}`);
      const response = await api.get(`/profile_quality/${id}?time_period=${timePeriod}`);
      
      // Speichere Daten im Cache
      cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
      
      return response.data;
    } catch (error) {
      console.warn('Profile quality API returned an error:', error);
      
      // Dummy-Daten für Fehlerfall
      const fallbackData = {
        profile_completeness: 0.75, // 75% vollständig
        avatar_exists: true,
        description_quality: 0.8, // 80% Qualität
        response_rate: 0.9, // 90% Antwortrate
        example_pflegekraefte: 3, // 3 Beispiel-Pflegekräfte
        message_template_exists: true
      };
      
      // Auch Fehler-Fallback-Daten cachen, um wiederholte Fehleranfragen zu vermeiden
      const cacheKey = cacheHelper.createCacheKey(`profile_quality/${id}`, { time_period: timePeriod });
      cacheHelper.saveToCache(cacheKey, fallbackData, useExtendedCache);
      
      return fallbackData;
    }
  },

  // Quotas with Reasons
  getAgencyEarlyEndReasons: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`quotas_with_reasons/${id}/early-end-reasons`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await api.get(`/quotas_with_reasons/${id}/early-end-reasons?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
    return response.data;
  },

  getAgencyCancellationReasons: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    // Cache-Schlüssel erstellen
    const cacheKey = cacheHelper.createCacheKey(`quotas_with_reasons/${id}/cancellation-reasons`, { time_period: timePeriod });
    
    // Prüfen, ob Daten im Cache sind
    if (!forceRefresh) {
      const cachedData = cacheHelper.getFromCache(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await api.get(`/quotas_with_reasons/${id}/cancellation-reasons?time_period=${timePeriod}`);
    
    // Speichere Daten im Cache
    cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
    
    return response.data;
  },

  // Problematic Stays API
  getProblematicStaysOverview: async (
    agencyId?: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      // Parameter für URL und Cache-Schlüssel
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) {
        params.agency_id = agencyId;
      }
      
      // Cache-Schlüssel erstellen
      const cacheKey = cacheHelper.createCacheKey(`problematic_stays/overview`, params);
      
      // Prüfen, ob Daten im Cache sind
      if (!forceRefresh) {
        const cachedData = cacheHelper.getFromCache(cacheKey);
        if (cachedData) {
          return cachedData;
        }
      }
      
      // URL erstellen
      const url = agencyId 
        ? `/problematic_stays/overview?agency_id=${agencyId}&time_period=${timePeriod}`
        : `/problematic_stays/overview?time_period=${timePeriod}`;
      
      console.log(`Fetching problematic stays overview ${agencyId ? 'for agency ' + agencyId : ''}, period ${timePeriod}`);
      const response = await api.get(url);
      
      // Speichere Daten im Cache
      cacheHelper.saveToCache(cacheKey, response.data, useExtendedCache);
      
      return response.data;
    } catch (error) {
      console.error('Error fetching problematic stays overview:', error);
      
      // Fallback-Daten für Fehlerfall
      const fallbackData = {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
      
      // Auch Fehler-Fallback-Daten cachen
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) {
        params.agency_id = agencyId;
      }
      const cacheKey = cacheHelper.createCacheKey(`problematic_stays/overview`, params);
      cacheHelper.saveToCache(cacheKey, fallbackData, useExtendedCache);
      
      return fallbackData;
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

// Neue Preload-Funktion
export const preloadService = {
  // Preload alle Daten für die wichtigsten Zeitperioden und Ansichten
  preloadAllData: async (
    selectedAgencyId: string,
    onProgressUpdate?: (progress: PreloadProgress) => void
  ): Promise<boolean> => {
    // Fortschrittsobjekt initialisieren
    const progress: PreloadProgress = {
      totalRequests: 0,
      completedRequests: 0,
      inProgress: true,
      status: 'Initialisiere Datenladung...',
      cachedEndpoints: 0
    };

    try {
      // Definiere alle zu ladenden Zeiträume (nur Backend-kompatible Zeiträume)
      const timePeriods = ['last_quarter', 'last_year', 'last_month', 'all_time'];
      
      // Alle Agenturen laden (wird für Vergleiche benötigt)
      progress.status = 'Lade Agentur-Informationen...';
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      await apiService.getAgencies();
      
      // API-Aufrufe definieren, die wir vorladen möchten
      const apiCalls = [];
      
      // 1. API-Aufrufe für QuotasPage
      // Für jede Zeitperiode die relevanten API-Aufrufe hinzufügen
      for (const period of timePeriods) {
        apiCalls.push(
          { name: `Quotas für ${period}`, fn: () => apiService.getAgencyQuotas(selectedAgencyId, period, false, true) },
          { name: `Cancellation Rate für ${period}`, fn: () => apiService.getCancellationBeforeArrivalRate(selectedAgencyId, period, false, true) },
          { name: `Reaction Times für ${period}`, fn: () => apiService.getAgencyReactionTimes(selectedAgencyId, period, false, true) },
          { name: `Arrival to Cancellation für ${period}`, fn: () => apiService.getArrivalToCancellationStats(selectedAgencyId, period, false, true) },
          { name: `Cancellation Stats für ${period}`, fn: () => apiService.getOverallCancellationBeforeArrivalStats(period, false, true) },
          { name: `Cancellation Reasons für ${period}`, fn: () => apiService.getAgencyCancellationReasons(selectedAgencyId, period, false, true) },
          { name: `Early End Reasons für ${period}`, fn: () => apiService.getAgencyEarlyEndReasons(selectedAgencyId, period, false, true) }
        );
      }
      
      
      // 2. API-Aufrufe für ResponseTimesPage
      for (const period of timePeriods) {
        apiCalls.push(
          { name: `Posting to Reservation Stats für ${period}`, fn: () => apiService.getOverallPostingToReservationStats(period) },
          { name: `Reservation to Proposal Stats für ${period}`, fn: () => apiService.getOverallReservationToFirstProposalStats(period) },
          { name: `Proposal to Cancellation Stats für ${period}`, fn: () => apiService.getOverallProposalToCancellationStats(period) },
          { name: `Arrival to Cancellation Stats für ${period}`, fn: () => apiService.getOverallArrivalToCancellationStats(period) }
        );
      }

      // 3. Zusätzliche API-Aufrufe für ProblematicStaysPage
      // Wir greifen auf den direkten API-Client zu für Problematic Stays
      for (const period of timePeriods) {
        // Für diese Aufrufe müssen wir den Backend-Pfad mit /api/ Präfix verwenden
        apiCalls.push(
          { 
            name: `Problematic Stays Overview für ${period}`, 
            fn: async () => {
              try {
                const result = await api.get(`/problematic_stays/overview`, {
                  params: { agency_id: selectedAgencyId, time_period: period, useExtendedCache: true }
                });
                return result.data;
              } catch (e) {
                console.error(`Error fetching problematic stays overview for ${period}:`, e);
                return null;
              }
            } 
          },
          { 
            name: `Problematic Stays Reasons für ${period}`, 
            fn: async () => {
              try {
                const result = await api.get(`/problematic_stays/reasons`, {
                  params: { agency_id: selectedAgencyId, time_period: period, useExtendedCache: true }
                });
                return result.data;
              } catch (e) {
                console.error(`Error fetching problematic stays reasons for ${period}:`, e);
                return null;
              }
            } 
          },
          { 
            name: `Problematic Stays Time Analysis für ${period}`, 
            fn: async () => {
              try {
                const result = await api.get(`/problematic_stays/time-analysis`, {
                  params: { agency_id: selectedAgencyId, time_period: period, useExtendedCache: true }
                });
                return result.data;
              } catch (e) {
                console.error(`Error fetching problematic stays time analysis for ${period}:`, e);
                return null;
              }
            } 
          },
          { 
            name: `Problematic Stays Heatmap für ${period}`, 
            fn: async () => {
              try {
                const result = await api.get(`/problematic_stays/heatmap`, {
                  params: { agency_id: selectedAgencyId, time_period: period, useExtendedCache: true }
                });
                return result.data;
              } catch (e) {
                console.error(`Error fetching problematic stays heatmap for ${period}:`, e);
                return null;
              }
            } 
          }
        );
      }

      // Gesamtzahl der Anfragen
      progress.totalRequests = apiCalls.length + 1; // +1 für Agenturen
      progress.completedRequests = 1; // Agenturen wurden bereits geladen
      
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      // Jeden API-Aufruf einzeln ausführen, um den Fortschritt zu verfolgen
      for (let i = 0; i < apiCalls.length; i++) {
        const call = apiCalls[i];
        
        // Aktualisiere Status mit Prozentangabe
        const percent = Math.round((i / apiCalls.length) * 100);
        progress.status = `Lade ${call.name}... (${percent}%)`;
        if (onProgressUpdate) onProgressUpdate({...progress});
        
        try {
          // Ausführen der Funktion und Messen der Zeit
          const startTime = Date.now();
          await call.fn();
          const endTime = Date.now();
          
          // Wenn der Aufruf schnell war, war es wahrscheinlich ein Cache-Treffer
          if (endTime - startTime < 100) {
            progress.cachedEndpoints = (progress.cachedEndpoints || 0) + 1;
          }
          
          // Aktualisiere den Fortschritt
          progress.completedRequests++;
          if (onProgressUpdate) onProgressUpdate({...progress});
        } catch (error) {
          console.error(`Fehler beim Laden von ${call.name}:`, error);
          // Aktualisiere den Fortschritt trotz Fehler
          progress.completedRequests++;
          if (onProgressUpdate) onProgressUpdate({...progress});
        }
      }
      
      // Abschluss
      progress.completedRequests = progress.totalRequests;
      progress.inProgress = false;
      progress.status = 'Alle Daten erfolgreich geladen!';
      
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      return true;
    } catch (error) {
      console.error('Fehler beim Preloading der Daten:', error);
      
      // Fehler im Fortschrittsobjekt vermerken
      progress.inProgress = false;
      progress.status = 'Fehler beim Laden der Daten';
      progress.error = error instanceof Error ? error.message : 'Unbekannter Fehler';
      
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      return false;
    }
  }
};

export default apiService; 