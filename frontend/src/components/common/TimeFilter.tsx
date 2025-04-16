import React from 'react';
import { useAppStore } from '../../store/appStore';

const TimeFilter: React.FC = () => {
  const { timePeriod, setTimePeriod } = useAppStore();
  
  const handleTimeFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTimePeriod(e.target.value);
  };
  
  return (
    <div className="time-filter">
      <select
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        value={timePeriod}
        onChange={handleTimeFilterChange}
      >
        <option value="last_quarter">Letztes Quartal</option>
        <option value="last_month">Letzter Monat</option>
        <option value="last_year">Letztes Jahr</option>
        <option value="all_time">Gesamter Zeitraum</option>
      </select>
    </div>
  );
};

export default TimeFilter; 