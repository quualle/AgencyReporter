import React from 'react';

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'problematic' | 'cancellations' | 'terminations';
}

const InfoModal: React.FC<InfoModalProps> = ({ isOpen, onClose, type }) => {
  if (!isOpen) return null;

  const getContent = () => {
    switch (type) {
      case 'problematic':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                Problematische Einsätze
              </h3>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                Diese Kennzahl vereint alle Pflegeeinsätze, bei denen es zu erheblichen Komplikationen kam:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border-l-4 border-red-500">
                <h4 className="font-semibold text-red-800 dark:text-red-300 mb-2 flex items-center">
                  <span className="mr-2">❌</span> Vor Anreise abgebrochen
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Einsätze, die trotz Bestätigung nicht stattfanden
                </p>
              </div>
              
              <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border-l-4 border-orange-500">
                <h4 className="font-semibold text-orange-800 dark:text-orange-300 mb-2 flex items-center">
                  <span className="mr-2">⏱️</span> Stark verkürzt (&gt;33%)
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Einsätze mit erheblicher Verkürzung der Aufenthaltsdauer
                </p>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <strong>💡 Hinweis:</strong> Diese Metrik zeigt die Gesamtqualität der Agenturleistung
              </p>
            </div>
          </div>
        );

      case 'cancellations':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
                <span className="text-2xl">🚌</span>
              </div>
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                Probleme vor der Anreise
              </h3>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                Erfasst werden Einsätze, die <strong>trotz Bestätigung</strong> vor der geplanten Anreise abgebrochen wurden.
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-sm">✓</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 dark:text-white">Status "Bestätigt" erreicht</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Alle Parteien gingen von einer sicheren Durchführung aus
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-sm">✗</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 dark:text-white">Vorzeitig abgebrochen</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Die zugesagte Sicherheit wurde durchbrochen
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
              <p className="text-sm text-amber-800 dark:text-amber-300">
                <strong>⚠️ Wichtig:</strong> Nur "bestätigte" Einsätze zählen - nicht bloße Vorschläge oder Akzeptanzen
              </p>
            </div>
          </div>
        );

      case 'terminations':
        return (
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center">
                <span className="text-2xl">🏠</span>
              </div>
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                Probleme nach der Anreise
              </h3>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                Erfasst werden <strong>angetretene</strong> Einsätze mit erheblicher Verkürzung nach erfolgter Anreise.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-semibold text-green-800 dark:text-green-300 mb-2">
                  ✈️ Anreise erfolgt
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Die Pflegekraft ist nachweislich angekommen
                </p>
              </div>
              
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 className="font-semibold text-red-800 dark:text-red-300 mb-2">
                  📉 Stark verkürzt (&gt;33%)
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Mindestens ein Drittel der geplanten Zeit wurde nicht erfüllt
                </p>
              </div>
            </div>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border-2 border-yellow-300 dark:border-yellow-700">
              <div className="flex items-start space-x-2">
                <span className="text-2xl">⚡</span>
                <div>
                  <h4 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-1">
                    Nur abgeschlossene Einsätze
                  </h4>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    <strong>Laufende Einsätze werden NICHT gezählt</strong>, da deren Ausgang noch unbekannt ist. 
                    Die Statistik basiert ausschließlich auf beendeten Pflegeeinsätzen.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <strong>📊 Statistisch relevant:</strong> Ab 33% Verkürzung ist von einem zugrundeliegenden Problem auszugehen
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              {getContent()}
            </div>
            <button
              onClick={onClose}
              className="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoModal;