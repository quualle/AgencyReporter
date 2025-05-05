import React, { useEffect, useState } from 'react';
import { useAppStore } from '../../store/appStore';
import apiService, { Agency } from '../../services/api';

// Erweitere das Agency Interface um das neue Flag
interface AgencyWithStatus extends Agency {
  is_active_recently: boolean;
}

const AgencySelector: React.FC = () => {
  const [agencies, setAgencies] = useState<AgencyWithStatus[]>([]); // Nutze erweitertes Interface
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const { selectedAgency, setSelectedAgency } = useAppStore();
  
  useEffect(() => {
    const fetchAgencies = async () => {
      try {
        setIsLoading(true);
        const data = await apiService.getAgencies(); // Holt jetzt Agenturen mit is_active_recently
        
        // Stelle sicher, dass is_active_recently immer boolean ist (default: false)
        const agenciesWithStatus: AgencyWithStatus[] = data.map(agency => ({
          ...agency,
          is_active_recently: agency.is_active_recently ?? false 
        }));
        
        setAgencies(agenciesWithStatus);
        
        // Standardmäßig Senioport auswählen oder zumindest eine aktive Agentur
        if (!selectedAgency && agenciesWithStatus.length > 0) {
          // Senioport hat die agency_id 649aa2dc2d847c6e7cbe0b56
          const senioport = agenciesWithStatus.find(a => a.agency_id === '649aa2dc2d847c6e7cbe0b56');
          const firstActive = agenciesWithStatus.find(a => a.is_active_recently);
          
          // Priorisiere Senioport > aktive Agentur > erste Agentur in der Liste
          setSelectedAgency(senioport || firstActive || agenciesWithStatus[0]);
        }
        
        setError(null);
      } catch (err) {
        setError('Fehler beim Laden der Agenturen');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAgencies();
  }, [selectedAgency, setSelectedAgency]); // Abhängigkeiten prüfen
  
  const handleAgencyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const agencyId = e.target.value;
    const agency = agencies.find(a => a.agency_id === agencyId);
    
    if (agency) {
      setSelectedAgency(agency);
    }
  };
  
  if (isLoading) {
    return (
      <div className="agency-selector animate-pulse">
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="agency-selector text-red-500">
        {error}
      </div>
    );
  }
  
  // Teile Agenturen in aktiv und inaktiv
  const activeAgencies = agencies.filter(a => a.is_active_recently);
  const inactiveAgencies = agencies.filter(a => !a.is_active_recently);
  
  return (
    <div className="agency-selector">
      <select
        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        value={selectedAgency?.agency_id || ''}
        onChange={handleAgencyChange}
      >
        <option value="" disabled>Agentur auswählen</option>
        {activeAgencies.length > 0 && (
          <optgroup label="Aktive Agenturen">
            {activeAgencies.map((agency) => (
              <option key={agency.agency_id} value={agency.agency_id}>
                {agency.agency_name}
              </option>
            ))}
          </optgroup>
        )}
        {inactiveAgencies.length > 0 && (
          <optgroup label="Inaktive Agenturen">
            {inactiveAgencies.map((agency) => (
              <option key={agency.agency_id} value={agency.agency_id}>
                {agency.agency_name}
              </option>
            ))}
          </optgroup>
        )}
      </select>
    </div>
  );
};

export default AgencySelector; 