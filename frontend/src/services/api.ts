import axios from 'axios';
import { calculateDateRange } from '../components/common/TimeFilter';

// Default API URL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Überprüfen der URL im Browser-Kontext
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

// Cache expiry times in hours
const STANDARD_CACHE_HOURS = 0.5; // 30 minutes
const EXTENDED_CACHE_HOURS = 2; // 2 hours

// Unified database cache helper
const databaseCache = {
  // Creates a consistent cache key
  createCacheKey: (endpoint: string, params: Record<string, any> = {}): string => {
    // Remove leading slash and sort parameters for consistency
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
    
    if (Object.keys(params).length === 0) {
      return `/${cleanEndpoint}`;
    }
    
    // Sort parameters alphabetically for consistency
    const sortedParams = Object.keys(params).sort().map(key => 
      `${key}=${params[key]}`
    ).join('&');
    
    return `/${cleanEndpoint}?${sortedParams}`;
  },
  
  // Get data from database cache
  getFromCache: async (cacheKey: string): Promise<any | null> => {
    try {
      // Encode the cache key for URL path parameter
      const encodedCacheKey = encodeURIComponent(cacheKey);
      const response = await api.get(`/cache/data/${encodedCacheKey}`);
      console.log(`✅ Database cache hit for: ${cacheKey}`);
      return response.data.data;
    } catch (error) {
      // Cache miss or error - return null
      return null;
    }
  },
  
  // Save data to database cache
  saveToCache: async (
    cacheKey: string, 
    data: any, 
    endpoint: string,
    agencyId?: string,
    timePeriod?: string,
    params?: Record<string, any>,
    useExtendedCache: boolean = false
  ): Promise<void> => {
    try {
      const expiresHours = useExtendedCache ? EXTENDED_CACHE_HOURS : STANDARD_CACHE_HOURS;
      
      const cacheData = {
        cache_key: cacheKey,
        data: data,
        endpoint: endpoint,
        agency_id: agencyId,
        time_period: timePeriod,
        params: params,
        expires_hours: expiresHours,
        is_preloaded: false
      };
      
      await api.post('/cache/save', cacheData);
      console.log(`💾 Saved to database cache: ${cacheKey}, expires in ${expiresHours * 60} minutes`);
    } catch (error) {
      console.error(`❌ Failed to save to database cache: ${cacheKey}`, error);
    }
  },

  // Extract agency ID and time period from endpoint and params
  extractMetadata: (endpoint: string, params: Record<string, any>) => {
    let agencyId: string | undefined;
    let timePeriod: string | undefined;
    
    // Extract agency ID from endpoint or params
    const agencyMatch = endpoint.match(/\/([a-f0-9]{24})\//);
    if (agencyMatch) {
      agencyId = agencyMatch[1];
    } else if (params.agency_id) {
      agencyId = params.agency_id;
    }
    
    // Extract time period from params
    if (params.time_period) {
      timePeriod = params.time_period;
    }
    
    return { agencyId, timePeriod };
  }
};

// Enhanced cached API call with unified cache handling
export const cachedApiCall = async (
  endpoint: string,
  params: Record<string, any> = {},
  options: {
    useExtendedCache?: boolean;
    forceRefresh?: boolean;
  } = {}
): Promise<any> => {
  const { useExtendedCache = false, forceRefresh = false } = options;
  
  // Create consistent cache key
  const cacheKey = databaseCache.createCacheKey(endpoint, params);
  
  // Extract metadata
  const { agencyId, timePeriod } = databaseCache.extractMetadata(endpoint, params);
  
  // Try database cache first (unless forcing refresh)
  if (!forceRefresh) {
    const cachedData = await databaseCache.getFromCache(cacheKey);
    if (cachedData) {
      return cachedData;
    }
  }
  
  // Make API call
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, String(value));
    }
  });
  
  const url = `${endpoint}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  console.log(`🔄 Fetching fresh data from: ${url}`);
  
  const response = await api.get(url);
  const data = response.data;
  
  // Save to database cache
  await databaseCache.saveToCache(
    cacheKey,
    data,
    endpoint,
    agencyId,
    timePeriod,
    params,
    useExtendedCache
  );
  
  return data;
};

// Interface for Preload progress and status
export interface PreloadProgress {
  totalRequests: number;
  completedRequests: number;
  inProgress: boolean;
  status: string;
  error?: string;
  cachedEndpoints?: number;
  sessionKey?: string;
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
  comparison_agency?: any;
  historical_data?: any;
}

// Helper function for custom date ranges
const calculateTimeRangeForPeriod = (timePeriod: string): { startDate: string, endDate: string } => {
  return calculateDateRange(timePeriod);
};

// API Service with unified cache handling
console.log('🚀 api.ts LOADED - NEW VERSION WITH PROBLEMATIC STAYS METHODS');

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
  getAgencyComparisonData: async (
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false, 
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const data = await cachedApiCall(
        '/agency_comparison',
        { time_period: timePeriod },
        { useExtendedCache, forceRefresh }
      );
      return data;
    } catch (error) {
      console.error('Error fetching agency comparison data:', error);
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
      const validTimePeriods = ['last_quarter', 'last_month', 'last_year', 'all_time'];
      
      if (validTimePeriods.includes(timePeriod)) {
        const data = await cachedApiCall(
          `/quotas/${id}/all`,
          { time_period: timePeriod },
          { useExtendedCache, forceRefresh }
        );
        
        console.log(`✅ Got quotas data for agency ${id}, period ${timePeriod}`);
        return data;
      } else {
        // For unsupported periods, use custom date range
        console.log(`Time period "${timePeriod}" not directly supported, converting to custom date range`);
        const { startDate, endDate } = calculateTimeRangeForPeriod(timePeriod);
        return await apiService.getAgencyQuotasWithCustomDates(id, startDate, endDate, forceRefresh, useExtendedCache);
      }
    } catch (error) {
      console.error(`Error fetching KPIs for agency ${id}:`, error);
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
  
  // Quotas with custom dates
  getAgencyQuotasWithCustomDates: async (
    id: string, 
    startDate: string, 
    endDate: string,
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const data = await cachedApiCall(
        `/quotas/${id}/all`,
        { start_date: startDate, end_date: endDate },
        { useExtendedCache, forceRefresh }
      );
      
      return data;
    } catch (error) {
      console.error(`Error fetching KPIs with custom dates for agency ${id}:`, error);
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
    const data = await cachedApiCall(
      `/quotas/${id}/cancellation-before-arrival`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
    
    return data;
  },

  // Reaction Times
  getAgencyReactionTimes: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    const data = await cachedApiCall(
      `/reaction_times/${id}`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
    
    console.log(`✅ Got reaction times for agency ${id}, period ${timePeriod}`);
    return data;
  },

  getPostingToReservationStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    return await cachedApiCall(`/reaction_times/${id}/posting_to_reservation`, { time_period: timePeriod });
  },

  getReservationToFirstProposalStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    return await cachedApiCall(`/reaction_times/${id}/reservation_to_first_proposal`, { time_period: timePeriod });
  },

  getProposalToCancellationStats: async (id: string, timePeriod: string = 'last_quarter'): Promise<any> => {
    return await cachedApiCall(`/reaction_times/${id}/proposal_to_cancellation`, { time_period: timePeriod });
  },

  getArrivalToCancellationStats: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    const data = await cachedApiCall(
      `/reaction_times/${id}/arrival_to_cancellation`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
    
    return data;
  },

  // Overall Average Stats
  getOverallPostingToReservationStats: async (
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false, 
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/reaction_times/stats/overall/posting_to_reservation`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getOverallReservationToFirstProposalStats: async (
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false, 
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/reaction_times/stats/overall/reservation_to_first_proposal`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getOverallProposalToCancellationStats: async (
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false, 
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/reaction_times/stats/overall/proposal_to_cancellation`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getOverallArrivalToCancellationStats: async (
    timePeriod: string = 'last_quarter', 
    forceRefresh: boolean = false, 
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/reaction_times/stats/overall/arrival_to_cancellation`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getOverallCancellationBeforeArrivalStats: async (
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/quotas/stats/overall/cancellation-before-arrival`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getAllAgenciesConversionStats: async (
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/quotas/all-agencies/conversion`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getAllAgenciesCompletionStats: async (
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/quotas/all-agencies/completion`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  // Comparison functions
  compareAgencyReactionTimes: async (id: string, timePeriod: string = 'last_quarter'): Promise<ComparisonData> => {
    const response = await api.post('/reaction_times/compare', { agency_id: id, time_period: timePeriod });
    return response.data;
  },

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
      const data = await cachedApiCall(
        `/profile_quality/${id}`,
        { time_period: timePeriod },
        { useExtendedCache, forceRefresh }
      );
      
      return data;
    } catch (error) {
      console.warn('Profile quality API returned an error:', error);
      
      // Fallback data
      const fallbackData = {
        profile_completeness: 0.75,
        avatar_exists: true,
        description_quality: 0.8,
        response_rate: 0.9,
        example_pflegekraefte: 3,
        message_template_exists: true
      };
      
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
    return await cachedApiCall(
      `/quotas_with_reasons/${id}/early-end-reasons`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  getAgencyCancellationReasons: async (
    id: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    return await cachedApiCall(
      `/quotas_with_reasons/${id}/cancellation-reasons`,
      { time_period: timePeriod },
      { useExtendedCache, forceRefresh }
    );
  },

  // Problematic Stays API
  getProblematicStaysOverview: async (
    agencyId?: string, 
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) {
        params.agency_id = agencyId;
      }
      
      const data = await cachedApiCall(
        `/problematic_stays/overview`,
        params,
        { useExtendedCache, forceRefresh }
      );
      
      console.log(`✅ Got problematic stays overview ${agencyId ? 'for agency ' + agencyId : ''}, period ${timePeriod}`);
      return data;
    } catch (error) {
      console.error('Error fetching problematic stays overview:', error);
      
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
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      if (eventType) params.event_type = eventType;
      
      return await cachedApiCall('/problematic_stays/reasons', params);
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
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      if (eventType) params.event_type = eventType;
      if (stayType) params.stay_type = stayType;
      
      return await cachedApiCall('/problematic_stays/time-analysis', params);
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
      const params: Record<string, any> = { time_period: timePeriod, limit };
      if (eventType) params.event_type = eventType;
      if (stayType) params.stay_type = stayType;
      
      return await cachedApiCall(`/problematic_stays/${agencyId}/detailed`, params);
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
  },

  // Additional Problematic Stays APIs
  getProblematicStaysHeatmap: async (
    agencyId?: string,
    eventType?: string,
    stayType?: string,
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      if (eventType) params.event_type = eventType;
      if (stayType) params.stay_type = stayType;
      
      return await cachedApiCall('/problematic_stays/heatmap', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays heatmap:', error);
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

  getProblematicStaysInstantDepartures: async (
    agencyId?: string,
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      
      return await cachedApiCall('/problematic_stays/instant-departures', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays instant departures:', error);
      return {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysReplacementAnalysis: async (
    agencyId?: string,
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      
      return await cachedApiCall('/problematic_stays/replacement-analysis', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays replacement analysis:', error);
      return {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysCustomerSatisfaction: async (
    agencyId?: string,
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      
      return await cachedApiCall('/problematic_stays/customer-satisfaction', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays customer satisfaction:', error);
      return {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  },

  getProblematicStaysTrendAnalysis: async (
    agencyId?: string,
    eventType?: string,
    stayType?: string,
    timePeriod: string = 'last_year',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      if (eventType) params.event_type = eventType;
      if (stayType) params.stay_type = stayType;
      
      return await cachedApiCall('/problematic_stays/trend-analysis', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays trend analysis:', error);
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

  getProblematicStaysCancellationLeadTime: async (
    agencyId?: string,
    timePeriod: string = 'last_quarter',
    forceRefresh: boolean = false,
    useExtendedCache: boolean = false
  ): Promise<any> => {
    try {
      const params: Record<string, any> = { time_period: timePeriod };
      if (agencyId) params.agency_id = agencyId;
      
      return await cachedApiCall('/problematic_stays/cancellation-lead-time', params, { useExtendedCache, forceRefresh });
    } catch (error) {
      console.error('Error fetching problematic stays cancellation lead time:', error);
      return {
        agency_id: agencyId || null,
        time_period: timePeriod,
        data: [],
        count: 0
      };
    }
  }
};

// Database Cache Service for management operations
export const databaseCacheService = {
  // Check data freshness for an agency
  checkDataFreshness: async (agencyId: string): Promise<any> => {
    try {
      const response = await api.get(`/cache/freshness/${agencyId}`);
      return response.data;
    } catch (error) {
      console.error('Error checking data freshness:', error);
      return { all_data_fresh: false, stale_data_types: [] };
    }
  },

  // Start preload session with freshness check
  startPreloadSession: async (agencyId: string): Promise<any> => {
    try {
      const response = await api.post(`/cache/preload/${agencyId}`);
      return response.data;
    } catch (error) {
      console.error('Error starting preload session:', error);
      throw error;
    }
  },

  // Start comprehensive preload session for ALL agencies and time periods
  startComprehensivePreload: async (): Promise<any> => {
    try {
      const response = await api.post('/cache/preload/comprehensive');
      return response.data;
    } catch (error) {
      console.error('Error starting comprehensive preload session:', error);
      throw error;
    }
  },

  // Execute comprehensive preload
  executeComprehensivePreload: async (): Promise<any> => {
    try {
      const response = await api.post('/cache/preload/comprehensive/execute');
      return response.data;
    } catch (error) {
      console.error('Error executing comprehensive preload:', error);
      throw error;
    }
  },

  // Get preload session info
  getPreloadSessionInfo: async (sessionKey: string): Promise<any> => {
    try {
      const response = await api.get(`/cache/preload/session/${sessionKey}`);
      return response.data;
    } catch (error) {
      console.error('Error getting preload session info:', error);
      return null;
    }
  },

  // Update preload session progress
  updatePreloadProgress: async (
    sessionKey: string, 
    totalRequests: number, 
    successfulRequests: number, 
    failedRequests: number
  ): Promise<boolean> => {
    try {
      await api.put(`/cache/preload/session/${sessionKey}/progress`, null, {
        params: {
          total_requests: totalRequests,
          successful_requests: successfulRequests,
          failed_requests: failedRequests
        }
      });
      return true;
    } catch (error) {
      console.error('Error updating preload progress:', error);
      return false;
    }
  },

  // Complete preload session
  completePreloadSession: async (sessionKey: string, success: boolean = true, errorMessage?: string): Promise<boolean> => {
    try {
      await api.put(`/cache/preload/session/${sessionKey}/complete`, null, {
        params: {
          success: success,
          error_message: errorMessage
        }
      });
      return true;
    } catch (error) {
      console.error('Error completing preload session:', error);
      return false;
    }
  },

  // Get cache statistics
  getCacheStats: async (): Promise<any> => {
    try {
      const response = await api.get('/cache/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return {};
    }
  }
};

// Enhanced Preload Service
export const preloadService = {
  // Comprehensive preload for ALL agencies and ALL time periods
  preloadComprehensiveData: async (
    onProgressUpdate?: (progress: PreloadProgress) => void
  ): Promise<boolean> => {
    const progress: PreloadProgress = {
      totalRequests: 1,
      completedRequests: 0,
      inProgress: true,
      status: 'Starte umfassende Datenladung für alle Agenturen...',
      cachedEndpoints: 0
    };

    try {
      if (onProgressUpdate) onProgressUpdate({...progress});

      progress.status = 'Initialisiere umfassende Datenladung...';
      if (onProgressUpdate) onProgressUpdate({...progress});

      const sessionData = await databaseCacheService.startComprehensivePreload();
      
      if (!sessionData.session_key) {
        throw new Error('Failed to start comprehensive preload session');
      }

      progress.status = 'Lade Daten für alle Agenturen und Zeiträume... (Dies kann 10-30 Minuten dauern)';
      if (onProgressUpdate) onProgressUpdate({...progress});

      const result = await databaseCacheService.executeComprehensivePreload();
      
      if (result.successful_requests > 0) {
        progress.status = `Umfassende Datenladung abgeschlossen! ${result.successful_requests}/${result.total_requests} erfolgreich geladen.`;
        progress.totalRequests = result.total_requests;
        progress.completedRequests = result.successful_requests;
        progress.inProgress = false;
        
        if (onProgressUpdate) onProgressUpdate({...progress});
        return true;
      } else {
        throw new Error('No data was successfully loaded');
      }

    } catch (error) {
      console.error('Comprehensive preload failed:', error);
      progress.status = 'Fehler bei der umfassenden Datenladung';
      progress.inProgress = false;
      progress.error = error instanceof Error ? error.message : 'Unbekannter Fehler';
      if (onProgressUpdate) onProgressUpdate({...progress});
      return false;
    }
  },

  // Agency-specific preload with freshness checking
  preloadAllDataWithDatabase: async (
    selectedAgencyId: string,
    onProgressUpdate?: (progress: PreloadProgress) => void
  ): Promise<boolean> => {
    const progress: PreloadProgress = {
      totalRequests: 1,
      completedRequests: 0,
      inProgress: true,
      status: 'Prüfe Datenaktualität...',
      cachedEndpoints: 0
    };

    try {
      if (onProgressUpdate) onProgressUpdate({...progress});

      // Check data freshness first
      const freshnessCheck = await databaseCacheService.checkDataFreshness(selectedAgencyId);
      
      if (freshnessCheck.all_data_fresh) {
        progress.status = 'Alle Daten sind bereits aktuell geladen!';
        progress.completedRequests = 1;
        progress.totalRequests = 1;
        progress.inProgress = false;
        progress.cachedEndpoints = freshnessCheck.freshness_details ? 
          Object.keys(freshnessCheck.freshness_details).length : 0;
        
        if (onProgressUpdate) onProgressUpdate({...progress});
        return true;
      }

      // Start preload session
      const sessionData = await databaseCacheService.startPreloadSession(selectedAgencyId);
      
      if (!sessionData.session_key) {
        throw new Error('Failed to start preload session');
      }

      const sessionKey = sessionData.session_key;
      progress.status = `Lade Daten für Agentur ${selectedAgencyId}...`;
      progress.sessionKey = sessionKey;
      if (onProgressUpdate) onProgressUpdate({...progress});

      // Load specific data for this agency
      const timePeriods = ['last_quarter', 'last_year', 'last_month', 'all_time'];
      const totalCalls = timePeriods.length * 7; // 7 different API types per period
      
      progress.totalRequests = totalCalls;
      let completed = 0;
      let successful = 0;
      let failed = 0;

      for (const period of timePeriods) {
        try {
          // Load key data for this agency and period
          await Promise.all([
            apiService.getAgencyQuotas(selectedAgencyId, period, false, true),
            apiService.getAgencyReactionTimes(selectedAgencyId, period, false, true),
            apiService.getArrivalToCancellationStats(selectedAgencyId, period, false, true),
            apiService.getAgencyCancellationReasons(selectedAgencyId, period, false, true),
            apiService.getAgencyEarlyEndReasons(selectedAgencyId, period, false, true),
            apiService.getCancellationBeforeArrivalRate(selectedAgencyId, period, false, true),
            apiService.getProblematicStaysOverview(selectedAgencyId, period, false, true),
            apiService.getProblematicStaysReasons(selectedAgencyId, undefined, period),
            apiService.getProblematicStaysTimeAnalysis(selectedAgencyId, undefined, undefined, period),
            apiService.getProblematicStaysHeatmap(selectedAgencyId, undefined, undefined, period, false, true),
            apiService.getProblematicStaysCustomerSatisfaction(selectedAgencyId, period, false, true)
          ]);
          
          successful += 7;
          completed += 7;
          
          progress.completedRequests = completed;
          progress.status = `Geladen: ${period} (${Math.round((completed / totalCalls) * 100)}%)`;
          if (onProgressUpdate) onProgressUpdate({...progress});

          // Update database session
          await databaseCacheService.updatePreloadProgress(sessionKey, totalCalls, successful, failed);
          
        } catch (error) {
          console.error(`Error loading data for period ${period}:`, error);
          failed += 7;
          completed += 7;
          progress.completedRequests = completed;
          if (onProgressUpdate) onProgressUpdate({...progress});
        }
      }

      // Complete session
      await databaseCacheService.completePreloadSession(sessionKey, successful > 0);
      
      progress.status = `Datenladung abgeschlossen! ${successful}/${totalCalls} erfolgreich geladen.`;
      progress.inProgress = false;
      if (onProgressUpdate) onProgressUpdate({...progress});

      return successful > 0;

    } catch (error) {
      console.error('Database preload failed:', error);
      progress.status = 'Fehler beim Laden der Daten';
      progress.inProgress = false;
      progress.error = error instanceof Error ? error.message : 'Unbekannter Fehler';
      if (onProgressUpdate) onProgressUpdate({...progress});
      return false;
    }
  }
};

export default apiService;