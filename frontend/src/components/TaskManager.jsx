import React, { useState, useEffect } from 'react';
import { Settings, Plus, Trash2, Edit2, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { fetchTasks, commitTasks } from '../lib/github';
import ScheduleManager from './ScheduleManager';

export default function TaskManager({ onOpenSettings }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [showSchedule, setShowSchedule] = useState(false);
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
      departure_date: '',
      return_date: '',
      expand_days: 0,
      max_stops: 1,
      max_duration_hours: 24,
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
          <button className="btn-secondary" onClick={() => setShowSchedule(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
             <Clock size={16} /> 排程設定
          </button>
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
      
      {showSchedule && <ScheduleManager onClose={() => setShowSchedule(false)} />}
      
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
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Outbound</span>
                  <div>{task.departure_date} {task.expand_days ? `(±1d)` : ''}</div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Inbound</span>
                  <div>{task.return_date || 'One-way'} {task.expand_days && task.return_date ? `(±1d)` : ''}</div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)', textTransform: 'uppercase', fontSize: '0.75rem' }}>Limits</span>
                  <div>Max {task.max_stops} stops, &lt;{task.max_duration_hours}h</div>
                </div>
                <div></div>
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
  
  const handleDateChange = (field, value) => {
    let newFormData = { ...formData, [field]: value };
    
    // Auto-fix return date if it's before departure
    if (field === 'departure_date' && newFormData.return_date && newFormData.return_date < value) {
      newFormData.return_date = value;
    } else if (field === 'return_date' && newFormData.departure_date && newFormData.departure_date > value) {
      newFormData.departure_date = value;
    }
    
    setFormData(newFormData);
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
      
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div>
          <label>Departure Date</label>
          <input type="date" value={formData.departure_date || formData.departure_date_range?.[0] || ''} onChange={e => handleDateChange('departure_date', e.target.value)} />
        </div>
        <div>
          <label>Return Date</label>
          <input type="date" value={formData.return_date || formData.arrive_period?.[0] || ''} onChange={e => handleDateChange('return_date', e.target.value)} />
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '0.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', margin: 0 }}>
            <input 
              type="checkbox" 
              checked={!!formData.expand_days} 
              onChange={e => handleChange('expand_days', e.target.checked ? 1 : 0)} 
              style={{ width: 'auto' }}
            />
            <span style={{ fontSize: '0.875rem' }}>彈性日期 (±1天)</span>
          </label>
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
          <label>Status</label>
          <select value={formData.active ? 'active' : 'paused'} onChange={e => handleChange('active', e.target.value === 'active')}>
            <option value="active">Active Monitoring</option>
            <option value="paused">Paused</option>
          </select>
        </div>
        <div></div>
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
