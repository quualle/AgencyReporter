import React from 'react';
import { useAppStore } from '../../store/appStore';
import AgencySelector from '../common/AgencySelector';

const Header: React.FC = () => {
  const { darkMode, toggleDarkMode } = useAppStore();

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-gray-800 dark:text-white mr-8">
            Agency Reporter
          </h1>
          
          <nav className="hidden md:flex">
            <ul className="flex space-x-6">
              <li>
                <a href="/" className="text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="/quotas" className="text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400">
                  Quoten
                </a>
              </li>
              <li>
                <a href="/response-times" className="text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400">
                  Reaktionszeiten
                </a>
              </li>
              <li>
                <a href="/quality" className="text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400">
                  Qualität
                </a>
              </li>
              <li>
                <a href="/strength-weakness" className="text-gray-600 hover:text-primary-500 dark:text-gray-300 dark:hover:text-primary-400">
                  Stärken/Schwächen
                </a>
              </li>
            </ul>
          </nav>
        </div>
        
        <div className="flex items-center space-x-4">
          <AgencySelector />
          
          <button 
            onClick={toggleDarkMode}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
          
          <button className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md">
            Export PDF
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 