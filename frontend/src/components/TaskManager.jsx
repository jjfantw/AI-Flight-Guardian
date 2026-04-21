import React, { useState, useEffect } from 'react';
import { Settings, Plus, Trash2, Edit2, CheckCircle2, AlertCircle } from 'lucide-react';
import { fetchTasks, commitTasks } from '../lib/github';

export default function TaskManager({ onOpenSettings }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    setLoading(true);
    try {
      const data = await fetchTasks();
      setTasks(data.tasks || []);
    } catch (e) {
      setError("Failed to load tasks. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  const handleSave = async (updatedTask) => {
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    // Update local state first
    let newTasks;
    if (editingTask && tasks.find(t => t.id === updatedTask.id)) {
      newTasks = tasks.map(t => t.id === updatedTask.id ? updatedTask : t);
    } else {
      newTasks = [...tasks, updatedTask];
    }
    
    try {
      await commitTasks({ tasks: newTasks });
      setTasks(newTasks);
      setEditingTask(null);
      setSuccess("Tasks successfully saved to GitHub!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (e) {
      setError("Failed to save to GitHub. Do you have a valid PAT configured?");
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if(!confirm("Are you sure you want to delete this task?")) return;
    setSaving(true);
    const newTasks = tasks.filter(t => t.id !== id);
    try {
      await commitTasks({ tasks: newTasks });
      setTasks(newTasks);
      setSuccess("Task deleted successfully.");
      setTimeout(() => setSuccess(null), 3000);
    } catch (e) {
      setError("Failed to delete from GitHub.");
    } finally {
      setSaving(false);
    }
  };

  const startNewTask = () => {
    setEditingTask({
      id: `task-${Date.now()}`,
      name: 'New Flight Plan',
      origin: [],
      destination: [],
      departure_date_range: ['', ''],
      trip_duration_days: [10, 14],
      max_stops: 1,
      max_duration_hours: 24,
      alert_threshold_price: 30000,
      active: true
    });
  };

  if(loading) return <div className="container" style={{ textAlign: 'center', marginTop: '4rem' }}>Loading Configuration...</div>;

  return (
    <div className="animate-fade-in">
      <div className="header">
        <div className="header-title">
          <Settings className="header-icon" />
          <h2>Manage Tracking Tasks</h2>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn-secondary" onClick={onOpenSettings}>
             GitHub Config
          </button>
          {!editingTask && (
            <button className="btn-primary" onClick={startNewTask}>
              <Plus size={18} /> Add New Task
            </button>
          )}
        </div>
      </div>
      
      {error && (
        <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
          <AlertCircle size={20} /> {error}
        </div>
      )}

      {success && (
        <div className="glass-panel" style={{ padding: '1rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
          <CheckCircle2 size={20} /> {success}
        </div>
      )}

      {editingTask ? (
        <TaskEditor 
          task={editingTask} 
          onSave={handleSave} 
          onCancel={() => setEditingTask(null)} 
          isSaving={saving} 
        />
      ) : (
        <div className="grid-2">
          {tasks.map(task => (
            <div key={task.id} className="glass-panel" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '4px' }}>
                    <h3 style={{ margin: 0 }}>{task.name}</h3>
                    <span className={`badge ${task.active ? 'badge-active' : 'badge-inactive'}`}>
                      {task.active ? 'Active' : 'Paused'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>ID: {task.id}</div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn-icon" onClick={() => setEditingTask({...task})}>
                    <Edit2 size={18} />
                  </button>
                  <button className="btn-icon btn-danger" onClick={() => handleDelete(task.id)}>
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.875rem' }}>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Route</span>
                  <div>{task.origin.join(',')} → {task.destination.join(',')}</div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Dates</span>
                  <div>{task.departure_date_range[0]} - {task.departure_date_range[1]}</div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Limits</span>
                  <div>Max {task.max_stops} stops, &lt;{task.max_duration_hours}h</div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Alert &lt;</span>
                  <div>{task.alert_threshold_price.toLocaleString()} TWD</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Child Component for Editing
function TaskEditor({ task, onSave, onCancel, isSaving }) {
  const [formData, setFormData] = useState(task);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field, textValue) => {
    const arr = textValue.split(',').map(s => s.trim()).filter(Boolean);
    handleChange(field, arr);
  };
  
  const handleRangeChange = (field, idx, value) => {
    const newRange = [...formData[field]];
    newRange[idx] = field.includes('date') ? value : Number(value);
    handleChange(field, newRange);
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <h3 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--panel-border)', paddingBottom: '1rem' }}>
        {task.id.startsWith('task-') ? 'Create New Task' : `Edit Task: ${task.name}`}
      </h3>
      
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div>
          <label>Task ID (unique string without spaces)</label>
          <input 
            value={formData.id} 
            onChange={e => handleChange('id', e.target.value)} 
            disabled={!task.id.startsWith('task-')}
          />
        </div>
        <div>
          <label>Task Name</label>
          <input value={formData.name} onChange={e => handleChange('name', e.target.value)} />
        </div>
      </div>
      
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div>
          <label>Origins (comma separated, e.g. TPE,KIX)</label>
          <input 
            value={formData.origin.join(', ')} 
            onChange={e => handleArrayChange('origin', e.target.value)} 
          />
        </div>
        <div>
          <label>Destinations (comma separated, e.g. CDG,AMS)</label>
          <input 
            value={formData.destination.join(', ')} 
            onChange={e => handleArrayChange('destination', e.target.value)} 
          />
        </div>
      </div>
      
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div>
          <label>Departure Period</label>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <input type="date" value={formData.departure_date_range[0]} onChange={e => handleRangeChange('departure_date_range', 0, e.target.value)} />
            <span style={{ color: 'var(--text-tertiary)' }}>to</span>
            <input type="date" value={formData.departure_date_range[1]} onChange={e => handleRangeChange('departure_date_range', 1, e.target.value)} />
          </div>
        </div>
        <div>
          <label>Trip Duration (Days)</label>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <input type="number" value={formData.trip_duration_days[0]} onChange={e => handleRangeChange('trip_duration_days', 0, e.target.value)} />
            <span style={{ color: 'var(--text-tertiary)' }}>to</span>
            <input type="number" value={formData.trip_duration_days[1]} onChange={e => handleRangeChange('trip_duration_days', 1, e.target.value)} />
          </div>
        </div>
      </div>
      
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div>
          <label>Max Stops</label>
          <input type="number" value={formData.max_stops} onChange={e => handleChange('max_stops', Number(e.target.value))} />
        </div>
        <div>
          <label>Max Total Flight Duration (Hours)</label>
          <input type="number" value={formData.max_duration_hours} onChange={e => handleChange('max_duration_hours', Number(e.target.value))} />
        </div>
      </div>
      
      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div>
          <label>Target Budget (Alert Threshold)</label>
          <input type="number" value={formData.alert_threshold_price} onChange={e => handleChange('alert_threshold_price', Number(e.target.value))} />
        </div>
        <div>
          <label>Status</label>
          <select value={formData.active ? 'active' : 'paused'} onChange={e => handleChange('active', e.target.value === 'active')}>
            <option value="active">Active Monitoring</option>
            <option value="paused">Paused</option>
          </select>
        </div>
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', borderTop: '1px solid var(--panel-border)', paddingTop: '1.5rem' }}>
        <button className="btn-secondary" onClick={onCancel} disabled={isSaving}>Cancel</button>
        <button className="btn-primary" onClick={() => onSave(formData)} disabled={isSaving}>
          {isSaving ? 'Saving to GitHub...' : 'Save Task'}
        </button>
      </div>
    </div>
  );
}
