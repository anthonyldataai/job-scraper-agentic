import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import LogViewer from './components/LogViewer';
import ConfigPanel from './components/ConfigPanel';
import ExternalInput from './components/ExternalInput';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'logs': return <LogViewer />;
      case 'config': return <ConfigPanel />;
      case 'external': return <ExternalInput />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        <div className="top-bar">
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-serif)', fontSize: '1.5rem', color: 'var(--primary)' }}>JobOS</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ width: 8, height: 8, background: 'var(--success)', borderRadius: '50%' }}></span>
            Connected to Agent Swarm
          </div>
        </div>
        <div className="content-area">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
