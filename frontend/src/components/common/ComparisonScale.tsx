import React from 'react';

interface ComparisonScaleProps {
  label: string;
  agencyValue: number | null | undefined;
  averageValue: number | null | undefined;
  agencyName?: string; // Optional agency name
  unit?: string; // e.g., 'Std.', '%'
  evaluationType?: 'lowerIsBetter' | 'higherIsBetter' | 'neutral'; // Added evaluationType
  formatValue: (value: number | null | undefined) => string; // Function to format the displayed value
  tooltip?: string;
}

const ComparisonScale: React.FC<ComparisonScaleProps> = ({
  label,
  agencyValue,
  averageValue,
  agencyName, // Destructure the new prop
  unit = '',
  evaluationType = 'lowerIsBetter',
  formatValue,
  tooltip
}) => {

  const numAgencyValue = (agencyValue !== null && agencyValue !== undefined) ? Number(agencyValue) : null;
  const numAverageValue = (averageValue !== null && averageValue !== undefined) ? Number(averageValue) : null;

  // N/A Card
  if (numAgencyValue === null || numAverageValue === null || isNaN(numAgencyValue) || isNaN(numAverageValue)) {
    return (
      <div className="dashboard-card relative p-4 flex flex-col items-center" title={tooltip}>
        <h3 className="text-md font-semibold mb-2 text-center text-gray-700 dark:text-gray-200">{label}</h3>
        <div className="text-xl font-bold text-gray-500 dark:text-gray-400 mt-4">
          N/A
        </div>
        <div className="text-sm text-gray-400 dark:text-gray-500 mt-1">
          Vergleich nicht möglich
        </div>
         {tooltip && <TooltipIcon />}
      </div>
    );
  }

  // Determine scale maximum (add buffer)
  const maxValue = Math.max(numAgencyValue, numAverageValue) * 1.2 || 10; 

  // Calculate percentage positions (0% at bottom, 100% at top)
  const agencyPosition = (numAgencyValue / maxValue) * 100;
  const averagePosition = (numAverageValue / maxValue) * 100;

  // Determine color based on evaluationType
  let isBetter = false;
  let agencyColor = 'bg-primary-500'; 
  let textColor = 'text-primary-600 dark:text-primary-400'; 

  if (evaluationType !== 'neutral') {
      isBetter = evaluationType === 'lowerIsBetter' 
          ? numAgencyValue <= numAverageValue 
          : numAgencyValue >= numAverageValue;
      agencyColor = isBetter ? 'bg-green-500' : 'bg-red-500';
      textColor = isBetter ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
  }
  
  const averageColor = 'bg-gray-500';

  return (
    <div className="dashboard-card relative p-4 flex flex-col items-center" title={tooltip}>
      <h3 className="text-md font-semibold mb-3 text-center text-gray-700 dark:text-gray-200">{label}</h3>
      
      {/* Vertical Scale Area */}
      <div className="relative h-24 w-10 flex justify-center my-2">
          {/* Scale Bar */}
          <div className="relative h-full w-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              {/* Average Marker (Line across) */}
              <div 
                  className={`absolute left-0 w-full h-0.5 ${averageColor}`}
                  style={{ bottom: `${Math.min(Math.max(averagePosition, 0), 100)}%` }}
                  title={`Durchschnitt: ${formatValue(numAverageValue)}`}
              ></div>
              {/* Agency Marker (Dot) */}
              <div 
                  className={`absolute left-1/2 -translate-x-1/2 w-3 h-3 ${agencyColor} rounded-full border-2 border-white dark:border-gray-800 shadow`}
                  style={{ bottom: `${Math.min(Math.max(agencyPosition, 0), 100)}%`, transform: 'translate(-50%, 50%)' }} // Adjust vertical position
                  title={`Agentur: ${formatValue(numAgencyValue)}`}
              >
              </div>
          </div>
      </div>

      {/* Value Labels */}
      <div className="text-center text-sm mt-2">
         <div className={`mb-1 ${textColor}`}>
           <span className="font-semibold">{agencyName || 'Agentur'}:</span>
           <span className="ml-1">{formatValue(numAgencyValue)}</span>
         </div>
         <div className="text-gray-600 dark:text-gray-300">
            <span className="font-semibold">Durchschnitt:</span>
            <span className="ml-1">{formatValue(numAverageValue)}</span>
         </div>
      </div>
      {tooltip && <TooltipIcon />}
    </div>
  );
};

const TooltipIcon: React.FC = () => (
    <span className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 cursor-help">
       <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
       </svg>
    </span>
);

export default ComparisonScale; 