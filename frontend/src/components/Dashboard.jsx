import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { fetchTasks, fetchRecords, triggerWorkflow } from '../lib/github';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Plane, AlertTriangle, TrendingDown, RefreshCw, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [records, setRecords] = useState({});
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [triggerStatus, setTriggerStatus] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchTasks();
        if (data && data.tasks) {
          setTasks(data.tasks);
          
          // Fetch records for active tasks
          const recordsMap = {};
          for (const task of data.tasks.filter(t => t.active)) {
            const csv = await fetchRecords(task.id);
            if (csv) {
              const res = Papa.parse(csv, { header: true, skipEmptyLines: true });
              if (res.data && res.data.length > 0) {
                 // Sort by timestamp
                 const sorted = res.data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                 
                 // Process data for charts
                 recordsMap[task.id] = sorted.map((row, idx) => ({
                   ...row,
                   dateShort: new Date(row.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
                   priceValue: parseInt(row.price, 10)
                 }));
              }
            }
          }
          setRecords(recordsMap);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerStatus(null);
    try {
      await triggerWorkflow();
      setTriggerStatus('success');
      setTimeout(() => setTriggerStatus(null), 3000);
    } catch (e) {
      console.error(e);
      alert("Failed to trigger workflow: " + e.message);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) return <div className="container" style={{ textAlign: 'center', marginTop: '4rem' }}>Loading Flight Data...</div>;

  return (
    <div className="animate-fade-in">
      <div className="header">
        <div className="header-title">
          <Plane className="header-icon" />
          <h2>Flight Price Dashboard</h2>
        </div>
        <button 
          className="button button-secondary" 
          onClick={handleTrigger} 
          disabled={triggering}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          {triggering ? (
            <RefreshCw size={18} className="animate-spin" />
          ) : triggerStatus === 'success' ? (
            <CheckCircle size={18} style={{ color: 'var(--success-color)' }} />
          ) : (
            <RefreshCw size={18} />
          )}
          {triggering ? 'Triggering...' : triggerStatus === 'success' ? 'Workflow Started' : 'Refresh Data'}
        </button>
      </div>
      
      {tasks.filter(t => t.active).length === 0 && (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <AlertTriangle size={48} style={{ color: 'var(--warning-color)', marginBottom: '1rem', marginInline: 'auto' }} />
          <h3>No Active Tasks</h3>
          <p style={{ color: 'var(--text-secondary)' }}>You don't have any active tracking tasks. Add some in the Task Manager.</p>
        </div>
      )}

      <div className="grid-2">
        {tasks.filter(t => t.active).map(task => {
          const taskData = records[task.id] || [];
          const currentPrice = taskData.length > 0 ? taskData[taskData.length - 1].priceValue : null;
          const minHistoryPrice = taskData.length > 0 ? Math.min(...taskData.map(d => d.priceValue)) : null;
          const isGoodDeal = currentPrice && currentPrice <= task.alert_threshold_price;

          return (
            <div key={task.id} className="glass-panel" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ margin: 0 }}>{task.name}</h3>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    {task.origin.join(', ')} → {task.destination.join(', ')}
                  </div>
                </div>
                {isGoodDeal && (
                  <div className="badge" style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: 'var(--success-color)', display: 'flex', alignItems: 'center', gap: '4px', alignSelf: 'flex-start' }}>
                    <TrendingDown size={14} /> Good Deal
                  </div>
                )}
              </div>
              
              <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Current Price</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: isGoodDeal ? 'var(--success-color)' : 'var(--text-primary)' }}>
                    {currentPrice ? `${currentPrice.toLocaleString()} TWD` : 'No Data'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Target Threshold</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {task.alert_threshold_price ? `${task.alert_threshold_price.toLocaleString()}` : '-'}
                  </div>
                </div>
              </div>

              {taskData.length > 0 ? (
                <div style={{ height: 250, marginTop: '1rem' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={taskData} margin={{ top: 5, right: 5, left: 15, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis 
                        dataKey="dateShort" 
                        stroke="var(--text-tertiary)" 
                        fontSize={12} 
                        tickLine={false}
                        axisLine={false}
                      />
                      <YAxis 
                        domain={['auto', 'auto']} 
                        stroke="var(--text-tertiary)" 
                        fontSize={12} 
                        tickFormatter={(value) => `$${value/1000}k`}
                        tickLine={false}
                        axisLine={false}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'var(--bg-color)', borderColor: 'var(--panel-border)', borderRadius: 8, color: 'var(--text-primary)' }}
                        itemStyle={{ color: 'var(--accent-color)' }}
                        formatter={(value) => [`${value.toLocaleString()} TWD`, 'Price']}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="priceValue" 
                        stroke="var(--accent-color)" 
                        strokeWidth={3}
                        dot={{ r: 4, strokeWidth: 0, fill: 'var(--accent-color)' }} 
                        activeDot={{ r: 6, fill: 'var(--bg-color)', stroke: 'var(--accent-color)', strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.1)', borderRadius: 8, border: '1px dashed var(--panel-border)', color: 'var(--text-secondary)' }}>
                  No flight records available yet.
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
