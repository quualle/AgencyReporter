import React, { useState } from 'react';
import html2pdf from 'html2pdf.js';
import { useAppStore } from '../../store/appStore';

interface ExportButtonProps {
  targetElementId: string;
  filename?: string;
  pageTitle?: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ 
  targetElementId, 
  filename = 'agentur-bericht', 
  pageTitle 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const { selectedAgency } = useAppStore();

  const handleExport = async () => {
    try {
      setIsExporting(true);
      
      // Get the target element to export
      const element = document.getElementById(targetElementId);
      if (!element) {
        throw new Error(`Element with ID "${targetElementId}" not found`);
      }
      
      // Create a clone to modify for print without affecting the UI
      const printElement = element.cloneNode(true) as HTMLElement;
      
      // Add page title and header
      if (pageTitle || selectedAgency) {
        const headerDiv = document.createElement('div');
        headerDiv.style.padding = '20px';
        headerDiv.style.marginBottom = '20px';
        headerDiv.style.borderBottom = '1px solid #e5e7eb';
        
        const titleElement = document.createElement('h1');
        titleElement.style.fontSize = '24px';
        titleElement.style.fontWeight = 'bold';
        titleElement.style.marginBottom = '8px';
        titleElement.textContent = pageTitle || 'Agentur-Bericht';
        
        const subtitleElement = document.createElement('h2');
        subtitleElement.style.fontSize = '18px';
        subtitleElement.style.color = '#6b7280';
        subtitleElement.textContent = selectedAgency?.agency_name || '';
        
        const dateElement = document.createElement('p');
        dateElement.style.fontSize = '14px';
        dateElement.style.color = '#9ca3af';
        dateElement.style.marginTop = '8px';
        dateElement.textContent = `Erstellt am: ${new Date().toLocaleDateString('de-DE')}`;
        
        headerDiv.appendChild(titleElement);
        headerDiv.appendChild(subtitleElement);
        headerDiv.appendChild(dateElement);
        
        printElement.insertBefore(headerDiv, printElement.firstChild);
      }
      
      // Configure PDF options
      const options = {
        margin: [15, 15, 15, 15],
        filename: `${filename}-${selectedAgency?.agency_name || 'unbekannt'}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      // Generate the PDF
      await html2pdf().from(printElement).set(options).save();
      
      setIsExporting(false);
    } catch (error) {
      console.error('Error exporting PDF:', error);
      setIsExporting(false);
      alert('Fehler beim Exportieren des PDFs. Bitte versuchen Sie es später erneut.');
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting || !selectedAgency}
      className={`px-4 py-2 rounded-md flex items-center ${
        isExporting || !selectedAgency 
          ? 'bg-gray-300 cursor-not-allowed text-gray-500' 
          : 'bg-primary-600 hover:bg-primary-700 text-white'
      } transition-colors`}
    >
      {isExporting ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Exportieren...
        </>
      ) : (
        <>
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          Als PDF exportieren
        </>
      )}
    </button>
  );
};

export default ExportButton; 