import React from 'react';
import { useAppStore } from '../../store/appStore';
import { subMonths, subYears, format, startOfMonth, endOfMonth, startOfYear, endOfYear } from 'date-fns';

// Hilfsfunktion zur Datumsberechnung
export const calculateDateRange = (timePeriod: string): { startDate: string, endDate: string } => {
    const now = new Date();
    let startDate: Date;
    const endDate: Date = now;

    switch (timePeriod) {
        case 'last_month':
            startDate = subMonths(now, 1);
            break;
        case 'last_quarter':
            startDate = subMonths(now, 3);
            break;
        case 'last_year':
            startDate = subYears(now, 1);
            break;
        case 'all_time':
            startDate = new Date(2000, 0, 1); // Frühes Datum für "all time"
            break;
        // Füge hier ggf. weitere Fälle hinzu (z.B. 'this_month', 'this_year')
        // case 'this_month':
        //     startDate = startOfMonth(now);
        //     break;
        // case 'this_year':
        //     startDate = startOfYear(now);
        //     break;
        default:
            startDate = subMonths(now, 3); // Default: last_quarter
    }

    return {
        startDate: format(startDate, 'yyyy-MM-dd'),
        endDate: format(endDate, 'yyyy-MM-dd'),
    };
};

const TimeFilter: React.FC = () => {
    const { timePeriod, setTimePeriod } = useAppStore();
    
    const handleTimePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setTimePeriod(e.target.value);
    };

    const { startDate, endDate } = calculateDateRange(timePeriod);

    return (
        <div className="time-filter flex flex-col items-start space-y-1">
            <select
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full md:w-auto"
                value={timePeriod}
                onChange={handleTimePeriodChange}
            >
                <option value="last_month">Letzter Monat</option>
                <option value="last_quarter">Letztes Quartal</option>
                <option value="last_year">Letztes Jahr</option>
                <option value="all_time">Gesamt</option>
                {/* Füge hier ggf. weitere Optionen hinzu */}
            </select>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 md:mt-0 md:ml-0">
                <div className="flex items-center">
                   <span className="w-12">Start:</span>
                   <span className="font-medium ml-1">{startDate}</span>
                </div>
                 <div className="flex items-center">
                   <span className="w-12">Ende:</span>
                   <span className="font-medium ml-1">{endDate}</span>
                 </div>
            </div>
        </div>
    );
};

export default TimeFilter; 