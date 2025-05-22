import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './styles/App.css';

// Import pages
import Dashboard from './pages/Dashboard';
import QuotasPage from './pages/QuotasPage';
import ResponseTimesPage from './pages/ResponseTimesPage';
import QualityPage from './pages/QualityPage';
import StrengthWeaknessPage from './pages/StrengthWeaknessPage';
import LLMAnalysisPage from './pages/LLMAnalysisPage';
import ProblematicStaysPage from './pages/ProblematicStaysPage';
import AgencyComparisonPage from './pages/AgencyComparisonPage';

// Import layout components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <div className="main-container">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quotas" element={<QuotasPage />} />
            <Route path="/response-times" element={<ResponseTimesPage />} />
            <Route path="/quality" element={<QualityPage />} />
            <Route path="/strength-weakness" element={<StrengthWeaknessPage />} />
            <Route path="/llm-analysis" element={<LLMAnalysisPage />} />
            <Route path="/problematic-stays" element={<ProblematicStaysPage />} />
            <Route path="/agency-comparison" element={<AgencyComparisonPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default App; 