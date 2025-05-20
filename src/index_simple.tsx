import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';

const SimpleApp = () => {
  return (
    <div className="app-container">
      <h1>Agency Reporter - Simple Test</h1>
      <p>This is a simple test to verify the app can start.</p>
    </div>
  );
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <SimpleApp />
  </React.StrictMode>
); 