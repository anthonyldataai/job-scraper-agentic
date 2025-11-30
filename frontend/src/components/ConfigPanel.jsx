import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function ConfigPanel() {
    const [config, setConfig] = useState({
        keywords: [],
        location: "",
        schedule_interval: "30",
        target_industries: [],
        enabled_sources: ['indeed', 'totaljobs', 'cwjobs', 'reed', 'glassdoor', 'linkedin']
    });
    const [loading, setLoading] = useState(true);
    const [saveStatus, setSaveStatus] = useState(null);
    const [scraperStatus, setScraperStatus] = useState({ state: 'IDLE', message: '' });
    const [logs, setLogs] = useState([]);
    const [polling, setPolling] = useState(false);

    useEffect(() => {
        fetchConfig();
    }, []);

    useEffect(() => {
        let interval;
        if (polling) {
            interval = setInterval(async () => {
                try {
                    const statusRes = await axios.get(`${API_URL}/status`);
                    setScraperStatus(statusRes.data);

                    const logsRes = await axios.get(`${API_URL}/logs?limit=10`);
                    setLogs(logsRes.data);

                    if (statusRes.data.state !== 'RUNNING') {
                        setPolling(false);
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [polling]);

    const fetchConfig = async () => {
        try {
            const res = await axios.get(`${API_URL}/config`);
            const configData = {};
            res.data.forEach(item => {
                try {
                    configData[item.key] = JSON.parse(item.value);
                } catch (e) {
                    configData[item.key] = item.value;
                }
            });
            setConfig(prev => ({ ...prev, ...configData }));
            setLoading(false);
        } catch (err) {
            console.error("Error fetching config:", err);
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setConfig({ ...config, [name]: value });
        setSaveStatus(null);
    };

    const getDisplayValue = (key) => {
        const val = config[key];
        if (Array.isArray(val)) return val.join(', ');
        return val || '';
    };

    const handleStringInput = (e, key) => {
        const val = e.target.value;
        setConfig({ ...config, [key]: val });
        setSaveStatus(null);
    };

    const handleSourceToggle = (source) => {
        const currentSources = Array.isArray(config.enabled_sources) ? config.enabled_sources : [];
        const newSources = currentSources.includes(source)
            ? currentSources.filter(s => s !== source)
            : [...currentSources, source];
        setConfig({ ...config, enabled_sources: newSources });
        setSaveStatus(null);
    };

    const saveConfig = async () => {
        setSaveStatus('saving');
        try {
            const payload = { ...config };
            const bulkData = [];

            ['keywords', 'target_industries'].forEach(key => {
                let val = payload[key];
                if (typeof val === 'string') {
                    val = JSON.stringify(val.split(',').map(s => s.trim()).filter(s => s));
                } else if (Array.isArray(val)) {
                    val = JSON.stringify(val);
                }
                bulkData.push({ key, value: val });
            });

            ['location', 'schedule_interval'].forEach(key => {
                bulkData.push({ key, value: payload[key] });
            });

            // Add enabled_sources
            bulkData.push({
                key: 'enabled_sources',
                value: JSON.stringify(payload.enabled_sources || [])
            });

            await axios.post(`${API_URL}/config/bulk`, bulkData);
            await fetchConfig();

            setSaveStatus('success');
            setTimeout(() => setSaveStatus(null), 3000);
        } catch (err) {
            console.error(err);
            setSaveStatus('error');
        }
    };

    const triggerRun = async () => {
        // Auto-save before running
        await saveConfig();

        try {
            await axios.post(`${API_URL}/run`);
            setPolling(true);
            setScraperStatus({ state: 'RUNNING', message: 'Starting...' });
        } catch (err) {
            alert("Error triggering run: " + (err.response?.data?.detail || err.message));
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading configuration...</div>;

    return (
        <div className="animate-fade-in max-w-3xl mx-auto">
            <h1>Configuration</h1>
            <div className="card mt-6 flex flex-col gap-6">

                <div className="form-group">
                    <label className="block mb-2 font-semibold text-primary">
                        Search Keywords (Comma Separated)
                    </label>
                    <p className="text-sm text-text-secondary mb-2">
                        The scraper will search for these roles.
                    </p>
                    <textarea
                        value={getDisplayValue('keywords')}
                        onChange={(e) => handleStringInput(e, 'keywords')}
                        placeholder="e.g. Technical Project Manager, Product Owner, Scrum Master"
                        rows={3}
                        className="w-full p-3 rounded-lg border-2 border-border bg-surface focus:border-accent focus:outline-none transition-colors"
                    />
                </div>

                <div className="form-group">
                    <label className="block mb-2 font-semibold text-primary">
                        Target Industries (Comma Separated)
                    </label>
                    <p className="text-sm text-text-secondary mb-2">
                        Jobs NOT in these industries will be filtered out by the AI.
                    </p>
                    <textarea
                        value={getDisplayValue('target_industries')}
                        onChange={(e) => handleStringInput(e, 'target_industries')}
                        placeholder="e.g. FinTech, Capital Markets, Asset Management"
                        rows={3}
                        className="w-full p-3 rounded-lg border-2 border-border bg-surface focus:border-accent focus:outline-none transition-colors"
                    />
                </div>

                <div className="form-group">
                    <label className="block mb-2 font-semibold text-primary">Location</label>
                    <input
                        name="location"
                        value={config.location}
                        onChange={handleChange}
                        placeholder="e.g. London, Remote"
                        className="w-full p-3 rounded-lg border-2 border-border bg-surface focus:border-accent focus:outline-none transition-colors"
                    />
                </div>

                <div className="form-group">
                    <label className="block mb-2 font-semibold text-primary">Job Sources to Scrape</label>
                    <p className="text-sm text-text-secondary mb-3">
                        Select which job sites you want to scrape. At least one must be selected.
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                        {[
                            { id: 'indeed', label: 'Indeed' },
                            { id: 'totaljobs', label: 'TotalJobs' },
                            { id: 'cwjobs', label: 'CWJobs' },
                            { id: 'reed', label: 'Reed' },
                            { id: 'glassdoor', label: 'Glassdoor' },
                            { id: 'linkedin', label: 'LinkedIn' }
                        ].map(source => (
                            <label key={source.id} className="flex items-center gap-2 p-3 rounded-lg border-2 border-border bg-surface hover:border-accent transition-colors cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={(config.enabled_sources || []).includes(source.id)}
                                    onChange={() => handleSourceToggle(source.id)}
                                    className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-accent"
                                />
                                <span className="text-sm font-medium">{source.label}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="form-group">
                    <label className="block mb-2 font-semibold text-primary">Schedule Interval (Minutes)</label>
                    <select
                        name="schedule_interval"
                        value={config.schedule_interval}
                        onChange={handleChange}
                        className="w-full p-3 rounded-lg border-2 border-border bg-surface focus:border-accent focus:outline-none transition-colors"
                    >
                        <option value="30">Every 30 Minutes</option>
                        <option value="60">Every 60 Minutes</option>
                        <option value="90">Every 90 Minutes</option>
                        <option value="120">Every 2 Hours</option>
                    </select>
                </div>

                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border">
                    <button
                        className="btn btn-primary min-w-[140px]"
                        onClick={saveConfig}
                        disabled={saveStatus === 'saving' || scraperStatus.state === 'RUNNING'}
                    >
                        {saveStatus === 'saving' ? 'Saving...' :
                            saveStatus === 'success' ? 'Saved ✓' :
                                'Save Settings'}
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={triggerRun}
                        disabled={scraperStatus.state === 'RUNNING'}
                    >
                        {scraperStatus.state === 'RUNNING' ? 'Scraper Running...' : 'Trigger Scraper Run Now'}
                    </button>

                    {saveStatus === 'success' && (
                        <span className="text-success text-sm font-medium animate-fade-in">
                            Settings saved successfully!
                        </span>
                    )}
                    {saveStatus === 'error' && (
                        <span className="text-error text-sm font-medium">
                            Error saving settings.
                        </span>
                    )}
                </div>

                {/* Log Viewer Section */}
                {(scraperStatus.state === 'RUNNING' || logs.length > 0) && (
                    <div className="mt-6 p-4 bg-black rounded-lg border border-gray-700 font-mono text-sm">
                        <div className="flex justify-between items-center mb-2 border-b border-gray-700 pb-2">
                            <span className="text-gray-400">Live Logs</span>
                            <span className={`px-2 py-0.5 rounded text-xs ${scraperStatus.state === 'RUNNING' ? 'bg-blue-900 text-blue-200 animate-pulse' :
                                scraperStatus.state === 'ERROR' ? 'bg-red-900 text-red-200' :
                                    'bg-green-900 text-green-200'
                                }`}>
                                {scraperStatus.state}
                            </span>
                        </div>
                        <div className="flex flex-col gap-1 max-h-60 overflow-y-auto">
                            {logs.map((log, i) => (
                                <div key={i} className="flex gap-2">
                                    <span className="text-gray-500 text-xs whitespace-nowrap">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </span>
                                    <span className={
                                        log.status === 'ERROR' ? 'text-red-400' :
                                            log.status === 'SUCCESS' ? 'text-green-400' :
                                                'text-gray-300'
                                    }>
                                        [{log.agent_name}] {log.message}
                                    </span>
                                </div>
                            ))}
                            {logs.length === 0 && <span className="text-gray-600 italic">Waiting for logs...</span>}
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}
