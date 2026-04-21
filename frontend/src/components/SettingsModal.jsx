import React, { useState, useEffect } from 'react';
import { X, Save, Shield } from 'lucide-react';

export default function SettingsModal({ onClose }) {
  const [token, setToken] = useState('');
  const [owner, setOwner] = useState('');
  const [repo, setRepo] = useState('');

  useEffect(() => {
    setToken(localStorage.getItem('gh_pat') || '');
    setOwner(localStorage.getItem('gh_owner') || 'jjfantw');
    setRepo(localStorage.getItem('gh_repo') || 'AI-Flight-Guardian');
  }, []);

  const handleSave = () => {
    localStorage.setItem('gh_pat', token);
    localStorage.setItem('gh_owner', owner);
    localStorage.setItem('gh_repo', repo);
    onClose();
    // Refresh to apply new credentials
    window.location.reload();
  };

  return (
    <div className="modal-overlay animate-fade-in">
      <div className="modal-content glass-panel">
        <div className="header modal-header">
          <div className="header-title">
            <Shield className="header-icon" />
            <h3>GitHub Settings</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-body">
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            To save tasks and prevent rate limits, please provide a GitHub Personal Access Token (PAT). This is stored locally in your browser.
          </p>
          
          <div>
            <label>GitHub PAT</label>
            <input 
              type="password" 
              value={token} 
              onChange={e => setToken(e.target.value)} 
              placeholder="ghp_xxxxxxxxxxxx"
            />
          </div>
          
          <div className="grid-2">
            <div>
              <label>Repository Owner</label>
              <input 
                type="text" 
                value={owner} 
                onChange={e => setOwner(e.target.value)} 
                placeholder="jjfantw"
              />
            </div>
            <div>
              <label>Repository Name</label>
              <input 
                type="text" 
                value={repo} 
                onChange={e => setRepo(e.target.value)} 
                placeholder="AI-Flight-Guardian"
              />
            </div>
          </div>
        </div>
        
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave}>
            <Save size={18} />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
