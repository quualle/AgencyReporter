import React from 'react';
import { useAppStore } from '../../store/appStore';
import { subMonths, subYears, format, startOfMonth, endOfMonth, startOfYear, endOfYear, startOfQuarter, endOfQuarter, addDays, subQuarters } from 'date-fns';

// Hilfsfunktion zur Berechnung des aktuellen Quartals
export const getCurrentQuarter = (date: Date = new Date()): number => {
    const month = date.getMonth();
    return Math.floor(month / 3) + 1;
};

// Hilfsfunktion zum Ermitteln des Quartalsbeginns
export const getQuarterStart = (date: Date = new Date()): Date => {
    const quarter = getCurrentQuarter(date);
    return new Date(date.getFullYear(), (quarter - 1) * 3, 1);
};

// Hilfsfunktion zum Ermitteln des Quartalsendes
export const getQuarterEnd = (date: Date = new Date()): Date => {
    const quarter = getCurrentQuarter(date);
    const endMonth = quarter * 3 - 1;
    const endDay = new Date(date.getFullYear(), endMonth + 1, 0).getDate();
    return new Date(date.getFullYear(), endMonth, endDay);
};

// Hilfsfunktion zur Datumsberechnung
export const calculateDateRange = (timePeriod: string): { startDate: string, endDate: string } => {
    const now = new Date();
    let startDate: Date;
    let endDate: Date = now;

    switch (timePeriod) {
        case 'current_month':
            startDate = startOfMonth(now);
            endDate = endOfMonth(now);
            break;
        case 'last_month':
            const lastMonth = subMonths(now, 1);
            startDate = startOfMonth(lastMonth);
            endDate = endOfMonth(lastMonth);
            break;
        case 'current_quarter':
            startDate = getQuarterStart(now);
            endDate = getQuarterEnd(now);
            break;
        case 'last_quarter':
            const lastQuarter = subQuarters(now, 1);
            startDate = getQuarterStart(lastQuarter);
            endDate = getQuarterEnd(lastQuarter);
            break;
        case 'current_year':
            startDate = startOfYear(now);
            endDate = now;
            break;
        case 'last_year':
            const lastYear = subYears(now, 1);
            startDate = startOfYear(lastYear);
            endDate = endOfYear(lastYear);
            break;
        case 'all_time':
            startDate = new Date(2000, 0, 1); // Frühes Datum für "all time"
            break;
        default:
            startDate = getQuarterStart(subQuarters(now, 1)); // Default: last_quarter
            endDate = getQuarterEnd(subQuarters(now, 1));
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
    
    // Hilfsfunktion zur Anzeige des Zeitraums im lesbaren Format
    const getReadableTimePeriod = (): string => {
        const now = new Date();
        const currentQuarter = getCurrentQuarter(now);
        const currentYear = now.getFullYear();
        
        switch (timePeriod) {
            case 'current_month':
                return `${format(now, 'MMMM yyyy')}`;
            case 'last_month':
                return `${format(subMonths(now, 1), 'MMMM yyyy')}`;
            case 'current_quarter':
                return `Q${currentQuarter} ${currentYear}`;
            case 'last_quarter':
                const lastQuarter = subQuarters(now, 1);
                return `Q${getCurrentQuarter(lastQuarter)} ${lastQuarter.getFullYear()}`;
            case 'current_year':
                return `${currentYear}`;
            case 'last_year':
                return `${currentYear - 1}`;
            case 'all_time':
                return 'Gesamt';
            default:
                return '';
        }
    };

    return (
        <div className="time-filter flex flex-col items-start space-y-1">
            <select
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full md:w-auto"
                value={timePeriod}
                onChange={handleTimePeriodChange}
            >
                <option value="current_quarter">Aktuelles Quartal</option>
                <option value="last_quarter">Letztes Quartal</option>
                <option value="current_year">Aktuelles Jahr</option>
                <option value="last_year">Letztes Jahr</option>
                <option value="current_month">Aktueller Monat</option>
                <option value="last_month">Letzter Monat</option>
                <option value="all_time">Gesamt</option>
            </select>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 md:mt-0 md:ml-0 flex">
                <div className="mr-3 font-semibold">{getReadableTimePeriod()}</div>
                <div className="flex flex-col">
                    <div className="flex items-center">
                       <span className="w-12">Start:</span>
                       <span className="font-medium ml-1">{format(new Date(startDate), 'dd.MM.yyyy')}</span>
                    </div>
                     <div className="flex items-center">
                       <span className="w-12">Ende:</span>
                       <span className="font-medium ml-1">{format(new Date(endDate), 'dd.MM.yyyy')}</span>
                     </div>
                </div>
            </div>
        </div>
    );
};

export default TimeFilter; 