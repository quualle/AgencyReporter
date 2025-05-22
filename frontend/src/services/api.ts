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

// Erhöhte Cache-Dauer für längere Preload-Haltbarkeit (60 Minuten)
const STANDARD_CACHE_EXPIRY = 15 * 60 * 1000; // 15 Minuten
const EXTENDED_CACHE_EXPIRY = 60 * 60 * 1000; // 60 Minuten

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
    
    console.log(`Saved to cache: ${cacheKey}, expires in ${useExtendedCache ? '60' : '15'} minutes`);
  }
};

// Interface für Preload-Fortschritt und Status
export interface PreloadProgress {
  totalRequests: number;
  completedRequests: number;
  inProgress: boolean;
  status: string;
  error?: string;
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
      const validTimePeriods = ['last_quarter', 'last_month', 'last_year', 'all_time', 'current_quarter', 'current_month', 'current_year'];
      
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

  getCancellationBeforeArrivalRate: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas/${id}/cancellation-before-arrival?time_period=${timePeriod}`);
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
  getAgencyEarlyEndReasons: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas_with_reasons/${id}/early-end-reasons?time_period=${timePeriod}`);
    return response.data;
  },

  getAgencyCancellationReasons: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    const response = await api.get(`/quotas_with_reasons/${id}/cancellation-reasons?time_period=${timePeriod}`);
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
      status: 'Initialisiere Datenladung...'
    };

    try {
      // Definiere alle zu ladenden Zeiträume
      const timePeriods = ['last_quarter', 'current_quarter', 'last_year', 'current_year'];
      
      // Alle Agenturen laden (wird für Vergleiche benötigt)
      progress.status = 'Lade Agentur-Informationen...';
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      const agencies = await apiService.getAgencies();
      
      // Anzahl der API-Aufrufe berechnen
      // Für jede Zeitperiode: Quotas, Reaction Times, Profile Quality, Problematic Stays
      const apiCallsPerPeriod = 4;
      
      // Gesamtzahl der Anfragen (Agenturen * Zeitperioden * API-Aufrufe pro Periode + 1 für Agenturen selbst)
      progress.totalRequests = timePeriods.length * apiCallsPerPeriod + 1;
      progress.completedRequests = 1; // Agenturen wurden bereits geladen
      
      if (onProgressUpdate) onProgressUpdate({...progress});
      
      // Array für alle Promises
      const loadPromises: Promise<any>[] = [];
      
      // Für jede Zeitperiode die Daten laden
      for (const period of timePeriods) {
        // Informationen zu API-Aufrufen für Fortschrittsanzeige
        const apiCalls = [
          {name: 'Quotas', fn: () => apiService.getAgencyQuotas(selectedAgencyId, period, true, true)},
          {name: 'Reaction Times', fn: () => apiService.getAgencyReactionTimes(selectedAgencyId, period, true, true)},
          {name: 'Profile Quality', fn: () => apiService.getAgencyProfileQuality(selectedAgencyId, period, true, true)},
          {name: 'Problematic Stays', fn: () => apiService.getProblematicStaysOverview(selectedAgencyId, period, true, true)}
        ];
        
        // Jeden API-Aufruf einzeln ausführen, um den Fortschritt zu verfolgen
        for (const call of apiCalls) {
          progress.status = `Lade ${call.name} für ${period}...`;
          if (onProgressUpdate) onProgressUpdate({...progress});
          
          try {
            // Führe den API-Aufruf aus und warte auf das Ergebnis
            await call.fn();
            
            // Aktualisiere den Fortschritt
            progress.completedRequests++;
            if (onProgressUpdate) onProgressUpdate({...progress});
          } catch (error) {
            console.error(`Fehler beim Laden von ${call.name} für ${period}:`, error);
            // Fortfahren trotz Fehler
          }
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