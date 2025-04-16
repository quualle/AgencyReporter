import React, { useEffect, useState } from 'react';
import { useAppStore } from '../../store/appStore';
import apiService, { Agency } from '../../services/api';

const AgencySelector: React.FC = () => {
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const { selectedAgency, setSelectedAgency } = useAppStore();
  
  useEffect(() => {
    const fetchAgencies = async () => {
      try {
        setIsLoading(true);
        const data = await apiService.getAgencies();
        setAgencies(data);
        
        // Auto-select the first agency if none is selected
        if (!selectedAgency && data.length > 0) {
          setSelectedAgency(data[0]);
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
  }, [selectedAgency, setSelectedAgency]);
  
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
  
  return (
    <div className="agency-selector">
      <select
        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        value={selectedAgency?.agency_id || ''}
        onChange={handleAgencyChange}
      >
        <option value="" disabled>Agentur auswählen</option>
        {agencies.map((agency) => (
          <option key={agency.agency_id} value={agency.agency_id}>
            {agency.agency_name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default AgencySelector; 