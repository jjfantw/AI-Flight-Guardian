import React, { useState, useEffect } from 'react';
import { Clock, Plus, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { fetchWorkflow, commitWorkflow } from '../lib/github';
import { extractTimesFromWorkflow, updateWorkflowTimes } from '../lib/cronUtils';

export default function ScheduleManager({ onClose }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [times, setTimes] = useState([]);
  const [workflowInfo, setWorkflowInfo] = useState(null);

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    setLoading(true);
    try {
      const data = await fetchWorkflow();
      if (!data) {
        setError("Failed to load workflow file. Note: A GitHub PAT with 'workflow' scope is required.");
        return;
      }
      setWorkflowInfo(data);
      const parsedTimes = extractTimesFromWorkflow(data.content);
      setTimes(parsedTimes);
    } catch (e) {
      setError("An error occurred while loading the schedule.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!workflowInfo) return;
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const newYaml = updateWorkflowTimes(workflowInfo.content, times);
      await commitWorkflow(newYaml, workflowInfo.sha);
      setSuccess("Schedule successfully updated!");
      // reload after 2 seconds to get fresh sha
      setTimeout(() => {
        loadSchedule();
      }, 2000);
    } catch (e) {
      setError("Failed to save. Have you added 'workflow' scope to your GitHub PAT?");
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleAddTime = () => {
    setTimes([...times, "12:00"]);
  };

  const handleRemoveTime = (index) => {
    const newTimes = [...times];
    newTimes.splice(index, 1);
    setTimes(newTimes);
  };

  const handleTimeChange = (index, val) => {
    const newTimes = [...times];
    newTimes[index] = val;
    setTimes(newTimes);
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      backdropFilter: 'blur(4px)'
    }}>
      <div className="glass-panel" style={{ width: '90%', maxWidth: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <Clock size={24} color="var(--primary-color)" /> Manage Schedule
        </h2>

        {error && (
          <div style={{ padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px', borderRadius: '8px' }}>
            <AlertCircle size={20} /> <span style={{ fontSize: '0.9rem' }}>{error}</span>
          </div>
        )}

        {success && (
          <div style={{ padding: '1rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px', borderRadius: '8px' }}>
            <CheckCircle2 size={20} /> <span style={{ fontSize: '0.9rem' }}>{success}</span>
          </div>
        )}

        <div style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <p>排定每天自動檢查機票的時間點。所有時間皆為 <strong>台灣時間 (UTC+8)</strong>。</p>
          <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.8 }}>
            ⚠️ 儲存時會直接修改 GitHub Actions 檔案，您的 GitHub PAT 必須具有 <code>workflow</code> 權限。
          </p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-tertiary)' }}>Loading schedule...</div>
        ) : (
          <div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
              {times.map((time, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(255,255,255,0.02)', padding: '0.5rem', borderRadius: '8px' }}>
                  <input
                    type="time"
                    value={time}
                    onChange={(e) => handleTimeChange(idx, e.target.value)}
                    style={{ flex: 1, padding: '0.5rem', fontSize: '1.1rem' }}
                  />
                  <button className="btn-icon btn-danger" onClick={() => handleRemoveTime(idx)} title="Delete Time">
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
              {times.length === 0 && (
                <div style={{ fontStyle: 'italic', color: 'var(--text-tertiary)' }}>No times configured. Action will not run automatically.</div>
              )}
            </div>
            
            <button className="btn-secondary" onClick={handleAddTime} style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
              <Plus size={18} /> Add Time Point
            </button>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: 'auto' }}>
          <button className="btn-secondary" onClick={onClose} disabled={saving}>Cancel</button>
          <button className="btn-primary" onClick={handleSave} disabled={saving || loading}>
            {saving ? 'Saving...' : 'Save Schedule'}
          </button>
        </div>
      </div>
    </div>
  );
}
