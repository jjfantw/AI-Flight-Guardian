import React, { useState } from 'react';
import { PlaneTakeoff, LayoutDashboard, ListTodo } from 'lucide-react';
import Dashboard from './components/Dashboard';
import TaskManager from './components/TaskManager';
import SettingsModal from './components/SettingsModal';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="container">
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ backgroundColor: 'var(--accent-color)', padding: '0.5rem', borderRadius: '12px', boxShadow: '0 4px 12px var(--accent-glow)' }}>
            <PlaneTakeoff color="white" size={24} />
          </div>
          <h1 style={{ margin: 0, fontSize: '1.5rem', letterSpacing: '-0.025em' }}>AI Flight Guardian</h1>
        </div>
        
        <div className="tabs" style={{ margin: 0, border: 'none', padding: 0 }}>
          <button 
            className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <LayoutDashboard size={18} /> Dashboard
          </button>
          <button 
            className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <ListTodo size={18} /> Task Settings
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'tasks' && <TaskManager onOpenSettings={() => setShowSettings(true)} />}
      </main>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </div>
  );
}

export default App;
