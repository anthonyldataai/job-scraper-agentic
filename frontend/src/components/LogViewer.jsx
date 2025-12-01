import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function LogViewer() {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const interval = setInterval(fetchLogs, 2000); // Poll every 2s
        fetchLogs();
        return () => clearInterval(interval);
    }, []);

    const fetchLogs = async () => {
        try {
            const res = await axios.get(`${API_URL}/logs?limit=100`);
            setLogs(res.data);
        } catch (err) {
            console.error("Error fetching logs:", err);
        }
    };

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                    <h1>Agent Logs</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Real-time activity from the agent swarm.</p>
                </div>
                <button
                    className="btn"
                    style={{ backgroundColor: '#ef4444', color: 'white', fontSize: '0.9rem' }}
                    onClick={async () => {
                        if (confirm('Clear all logs?')) {
                            await axios.delete(`${API_URL}/logs`);
                            fetchLogs();
                        }
                    }}
                >
                    Clear Logs
                </button>
            </div>

            <div className="card" style={{ background: '#1e293b', color: '#e2e8f0', minHeight: '500px', maxHeight: '80vh', overflowY: 'auto' }}>
                {logs.map((log, idx) => (
                    <div key={idx} className={`log-entry log-${log.status}`}>
                        <span style={{ opacity: 0.5, marginRight: '1rem' }}>{new Date(log.timestamp).toLocaleTimeString()}</span>
                        <span style={{ fontWeight: 600, marginRight: '0.5rem' }}>[{log.agent_name}]</span>
                        {log.message}
                    </div>
                ))}
                {logs.length === 0 && <div style={{ padding: '1rem', opacity: 0.5 }}>No logs yet...</div>}
            </div>
        </div>
    );
}
