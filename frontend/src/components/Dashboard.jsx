import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Dashboard() {
    const [jobs, setJobs] = useState([]);
    const [sortBy, setSortBy] = useState('match_score');
    const [sortOrder, setSortOrder] = useState('desc');
    const [selectedJobs, setSelectedJobs] = useState(new Set());
    const [filters, setFilters] = useState({
        title: '',
        company: '',
        salary: '',
        source: '',
        score: '',
        date: '',
        added_at: ''
    });

    // --- Layout State & Persistence ---
    const initialColumns = [
        { id: 'select', label: '', width: 30, fixed: true },
        { id: 'score', label: 'Score', width: 80, sortable: true },
        { id: 'title', label: 'Title', width: 250, sortable: true, filterable: true },
        { id: 'company', label: 'Company', width: 150, sortable: true, filterable: true },
        { id: 'salary', label: 'Salary', width: 100, sortable: true },
        { id: 'posted_date', label: 'Posted', width: 100, sortable: true, filterable: true },
        { id: 'created_at', label: 'Added', width: 100, sortable: true, filterable: true },
        { id: 'reasoning', label: 'Reasoning', width: 300 },
        { id: 'actions', label: 'Actions', width: 120, fixed: true }
    ];

    const [columnOrder, setColumnOrder] = useState(initialColumns.map(c => c.id));
    const [columnWidths, setColumnWidths] = useState(
        initialColumns.reduce((acc, col) => ({ ...acc, [col.id]: col.width }), {})
    );
    const [rowHeight, setRowHeight] = useState('normal'); // compact, normal, comfortable
    const [showSettings, setShowSettings] = useState(false);

    // Helper to save to backend
    const saveLayoutToBackend = async (settings) => {
        try {
            await axios.post(`${API_URL}/config`, {
                key: 'dashboard_layout',
                value: JSON.stringify(settings)
            });
        } catch (err) {
            console.error("Error saving layout to backend:", err);
        }
    };

    // Load settings from Backend (with fallback to localStorage)
    useEffect(() => {
        const loadLayout = async () => {
            try {
                // Try fetching from backend first
                const res = await axios.get(`${API_URL}/config`);
                const layoutConfig = res.data.find(c => c.key === 'dashboard_layout');

                if (layoutConfig) {
                    try {
                        const parsed = JSON.parse(layoutConfig.value);
                        if (parsed.columnOrder) setColumnOrder(parsed.columnOrder);
                        if (parsed.columnWidths) setColumnWidths(prev => ({ ...prev, ...parsed.columnWidths }));
                        if (parsed.rowHeight) setRowHeight(parsed.rowHeight);
                        return; // Successfully loaded from backend
                    } catch (e) {
                        console.error("Failed to parse backend layout settings", e);
                    }
                }

                // Fallback to localStorage (Migration path)
                const savedLayout = localStorage.getItem('jobos_dashboard_layout');
                if (savedLayout) {
                    try {
                        const parsed = JSON.parse(savedLayout);
                        if (parsed.columnOrder) setColumnOrder(parsed.columnOrder);
                        if (parsed.columnWidths) setColumnWidths(prev => ({ ...prev, ...parsed.columnWidths }));
                        if (parsed.rowHeight) setRowHeight(parsed.rowHeight);

                        // Migrate to backend immediately
                        saveLayoutToBackend(parsed);
                    } catch (e) {
                        console.error("Failed to load local layout settings", e);
                    }
                }
            } catch (err) {
                console.error("Error loading layout config:", err);
            }
        };
        loadLayout();
        fetchJobs();
    }, []);

    // Save settings (Debounced)
    useEffect(() => {
        const settings = { columnOrder, columnWidths, rowHeight };

        // Always save to localStorage for immediate redundancy
        localStorage.setItem('jobos_dashboard_layout', JSON.stringify(settings));

        // Debounce save to backend
        const timeoutId = setTimeout(() => {
            saveLayoutToBackend(settings);
        }, 1000);

        return () => clearTimeout(timeoutId);
    }, [columnOrder, columnWidths, rowHeight]);

    const fetchJobs = async () => {
        try {
            const res = await axios.get(`${API_URL}/jobs`);
            setJobs(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    // --- Drag & Drop Logic ---
    const [draggedColumn, setDraggedColumn] = useState(null);

    const handleDragStart = (e, colId) => {
        setDraggedColumn(colId);
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e, targetColId) => {
        e.preventDefault();
        if (!draggedColumn || draggedColumn === targetColId) return;

        const newOrder = [...columnOrder];
        const draggedIdx = newOrder.indexOf(draggedColumn);
        const targetIdx = newOrder.indexOf(targetColId);

        newOrder.splice(draggedIdx, 1);
        newOrder.splice(targetIdx, 0, draggedColumn);

        setColumnOrder(newOrder);
    };

    const handleDragEnd = () => {
        setDraggedColumn(null);
    };

    // --- Resize Logic ---
    const handleMouseDown = (e, colId) => {
        e.preventDefault();
        const startX = e.pageX;
        const startWidth = columnWidths[colId];

        const handleMouseMove = (moveEvent) => {
            const deltaX = moveEvent.pageX - startX;
            setColumnWidths(prev => ({
                ...prev,
                [colId]: Math.max(50, startWidth + deltaX)
            }));
        };

        const handleMouseUp = () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    };

    const handleSort = (field) => {
        if (sortBy === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortOrder('desc');
        }
    };

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({ ...prev, [field]: value }));
    };

    const toggleSelectAll = () => {
        if (selectedJobs.size === filteredJobs.length) {
            setSelectedJobs(new Set());
        } else {
            setSelectedJobs(new Set(filteredJobs.map(j => j.id)));
        }
    };

    const toggleSelectJob = (id) => {
        const newSelected = new Set(selectedJobs);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelectedJobs(newSelected);
    };

    const deleteSelected = async () => {
        if (selectedJobs.size === 0) return;
        if (!confirm(`Delete ${selectedJobs.size} jobs?`)) return;

        try {
            await axios.delete(`${API_URL}/jobs`, { data: Array.from(selectedJobs) });
            setSelectedJobs(new Set());
            fetchJobs();
        } catch (err) {
            alert('Error deleting jobs: ' + err.message);
        }
    };

    const updateJob = async (id, data) => {
        try {
            await axios.patch(`${API_URL}/jobs/${id}`, data);
            fetchJobs();
        } catch (err) {
            console.error(err);
        }
    };

    const handleThumbsUp = async (job) => {
        const comment = prompt("Any additional feedback? (Optional)", job.user_feedback_comment || "Great fit!");
        if (comment === null) return; // Cancelled

        // 1. Save feedback
        await updateJob(job.id, { user_feedback_comment: comment });

        // 2. Analyze
        try {
            alert("Analyzing feedback... this may take a moment.");
            await axios.post(`${API_URL}/jobs/${job.id}/analyze_feedback`);
            fetchJobs();
            alert("Reasoning updated based on your feedback!");
        } catch (err) {
            alert("Error analyzing feedback: " + err.message);
        }
    };

    const filteredJobs = jobs.filter(job => {
        // Text filters
        const matchesText = (
            job.title.toLowerCase().includes(filters.title.toLowerCase()) &&
            job.company.toLowerCase().includes(filters.company.toLowerCase()) &&
            (job.salary || '').toLowerCase().includes(filters.salary.toLowerCase()) &&
            (job.source || '').toLowerCase().includes(filters.source.toLowerCase())
        );

        // Score filter
        let matchesScore = true;
        if (filters.score) {
            const score = job.match_score;
            const [min, max] = filters.score.split('-').map(Number);
            matchesScore = score >= min && score <= max;
        }

        // Date filter (Posted Date)
        let matchesDate = true;
        if (filters.date && job.posted_date) {
            const jobDate = new Date(job.posted_date);
            const today = new Date();
            const diffTime = Math.abs(today - jobDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (filters.date === '14+') {
                matchesDate = diffDays > 14;
            } else if (filters.date === '7-14') {
                matchesDate = diffDays >= 7 && diffDays <= 14;
            } else {
                matchesDate = diffDays <= parseInt(filters.date);
            }
        }

        // Added At filter
        let matchesAdded = true;
        if (filters.added_at && job.created_at) {
            const addedDate = new Date(job.created_at);
            const now = new Date();
            const diffMs = now - addedDate;
            const diffHours = diffMs / (1000 * 60 * 60);

            if (filters.added_at === '1h') matchesAdded = diffHours <= 1;
            else if (filters.added_at === '6h') matchesAdded = diffHours <= 6;
            else if (filters.added_at === '24h') matchesAdded = diffHours <= 24;
            else if (filters.added_at === 'today') {
                matchesAdded = addedDate.toDateString() === now.toDateString();
            }
            else if (filters.added_at === 'yesterday') {
                const yesterday = new Date(now);
                yesterday.setDate(yesterday.getDate() - 1);
                matchesAdded = addedDate.toDateString() === yesterday.toDateString();
            }
        }

        return matchesText && matchesScore && matchesDate && matchesAdded;
    });

    const sortedJobs = [...filteredJobs].sort((a, b) => {
        let aVal = a[sortBy];
        let bVal = b[sortBy];

        if (sortBy === 'posted_date' || sortBy === 'created_at') {
            aVal = aVal ? new Date(aVal) : new Date(0);
            bVal = bVal ? new Date(bVal) : new Date(0);
        }

        if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        const today = new Date();
        const diffTime = Math.abs(today - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    };

    const formatTime = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const [scraperStatus, setScraperStatus] = useState({ state: 'IDLE', message: '' });
    const [polling, setPolling] = useState(false);

    useEffect(() => {
        let interval;
        if (polling) {
            interval = setInterval(async () => {
                try {
                    const statusRes = await axios.get(`${API_URL}/status`);
                    setScraperStatus(statusRes.data);
                    if (statusRes.data.state !== 'RUNNING') {
                        setPolling(false);
                        fetchJobs(); // Refresh jobs when done
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [polling]);

    const triggerRun = async () => {
        try {
            await axios.post(`${API_URL}/run`);
            setPolling(true);
            setScraperStatus({ state: 'RUNNING', message: 'Starting...' });
        } catch (err) {
            alert("Error triggering run: " + (err.response?.data?.detail || err.message));
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    };

    const getRowHeightStyle = () => {
        switch (rowHeight) {
            case 'compact': return { padding: '0.25rem 0.5rem', fontSize: '0.85rem' };
            case 'comfortable': return { padding: '1rem', fontSize: '1rem' };
            default: return { padding: '0.75rem', fontSize: '0.9rem' };
        }
    };

    const renderHeaderCell = (colId) => {
        const colDef = initialColumns.find(c => c.id === colId) || {};
        const width = columnWidths[colId];

        return (
            <th
                key={colId}
                draggable={!colDef.fixed}
                onDragStart={(e) => !colDef.fixed && handleDragStart(e, colId)}
                onDragOver={(e) => !colDef.fixed && handleDragOver(e, colId)}
                onDragEnd={handleDragEnd}
                style={{
                    width: width,
                    position: 'relative',
                    cursor: colDef.fixed ? 'default' : 'move',
                    userSelect: 'none'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    {colDef.sortable ? (
                        <div onClick={() => {
                            const fieldMap = {
                                'score': 'match_score',
                                'posted_date': 'posted_date',
                                'created_at': 'created_at'
                            };
                            const field = fieldMap[colId] || colId;
                            handleSort(field);
                        }} style={{ cursor: 'pointer', fontWeight: 600 }}>
                            {colDef.label} {(() => {
                                const fieldMap = {
                                    'score': 'match_score',
                                    'posted_date': 'posted_date',
                                    'created_at': 'created_at'
                                };
                                const field = fieldMap[colId] || colId;
                                return sortBy === field && (sortOrder === 'asc' ? '↑' : '↓');
                            })()}
                        </div>
                    ) : (
                        <div style={{ fontWeight: 600 }}>{colDef.label}</div>
                    )}
                </div>

                {/* Filters */}
                {
                    colId === 'select' && (
                        <input
                            type="checkbox"
                            checked={filteredJobs.length > 0 && selectedJobs.size === filteredJobs.length}
                            onChange={toggleSelectAll}
                        />
                    )
                }
                {
                    colId === 'score' && (
                        <select
                            value={filters.score || ''}
                            onChange={(e) => handleFilterChange('score', e.target.value)}
                            style={{ width: '100%', padding: '2px', marginTop: '4px', fontSize: '0.75rem' }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <option value="">All</option>
                            <option value="90-100">90 - 100</option>
                            <option value="71-90">71 - 90</option>
                            <option value="51-70">51 - 70</option>
                            <option value="31-50">31 - 50</option>
                            <option value="0-30">0 - 30</option>
                        </select>
                    )
                }
                {
                    colId === 'title' && (
                        <input
                            type="text"
                            placeholder="Filter..."
                            value={filters.title}
                            onChange={(e) => handleFilterChange('title', e.target.value)}
                            style={{ width: '100%', padding: '4px', marginTop: '4px', fontSize: '0.8rem' }}
                            onClick={(e) => e.stopPropagation()}
                        />
                    )
                }
                {
                    colId === 'company' && (
                        <input
                            type="text"
                            placeholder="Filter..."
                            value={filters.company}
                            onChange={(e) => handleFilterChange('company', e.target.value)}
                            style={{ width: '100%', padding: '4px', marginTop: '4px', fontSize: '0.8rem' }}
                            onClick={(e) => e.stopPropagation()}
                        />
                    )
                }
                {
                    colId === 'posted_date' && (
                        <select
                            value={filters.date || ''}
                            onChange={(e) => handleFilterChange('date', e.target.value)}
                            style={{ width: '100%', padding: '2px', marginTop: '4px', fontSize: '0.75rem' }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <option value="">All</option>
                            <option value="1">Last 24 hours</option>
                            <option value="3">Last 3 days</option>
                            <option value="5">Last 5 days</option>
                            <option value="7">Last 7 days</option>
                            <option value="7-14">1 - 2 weeks ago</option>
                            <option value="14+">Older than 2 weeks</option>
                        </select>
                    )
                }
                {
                    colId === 'created_at' && (
                        <select
                            value={filters.added_at || ''}
                            onChange={(e) => handleFilterChange('added_at', e.target.value)}
                            style={{ width: '100%', padding: '2px', marginTop: '4px', fontSize: '0.75rem' }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <option value="">All</option>
                            <option value="1h">Last 1 Hour</option>
                            <option value="6h">Last 6 Hours</option>
                            <option value="24h">Last 24 Hours</option>
                            <option value="today">Today</option>
                            <option value="yesterday">Yesterday</option>
                        </select>
                    )
                }

                {/* Resizer Handle */}
                {
                    !colDef.fixed && (
                        <div
                            style={{
                                position: 'absolute',
                                right: 0,
                                top: 0,
                                bottom: 0,
                                width: '5px',
                                cursor: 'col-resize',
                                zIndex: 10
                            }}
                            onMouseDown={(e) => handleMouseDown(e, colId)}
                        />
                    )
                }
            </th >
        );
    };

    const renderCell = (job, colId) => {
        const style = { ...getRowHeightStyle(), color: 'var(--text-secondary)' };

        switch (colId) {
            case 'select':
                return (
                    <td style={{ ...style, textAlign: 'center' }}>
                        <input
                            type="checkbox"
                            checked={selectedJobs.has(job.id)}
                            onChange={() => toggleSelectJob(job.id)}
                        />
                    </td>
                );
            case 'score':
                return (
                    <td style={{ ...style, textAlign: 'center' }}>
                        <div style={{
                            width: '32px', height: '32px', borderRadius: '50%',
                            background: getScoreColor(job.match_score),
                            color: 'white', fontWeight: 'bold',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto'
                        }}>
                            {job.match_score}
                        </div>
                    </td>
                );
            case 'title':
                return (
                    <td style={style}>
                        <a href={job.link} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 600, color: 'var(--primary)', textDecoration: 'none' }}>
                            {job.title}
                        </a>
                        <div style={{
                            fontSize: '0.8rem',
                            opacity: 0.7,
                            display: '-webkit-box',
                            WebkitLineClamp: 4,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                        }}>
                            {job.location} • {job.source}
                        </div>
                    </td>
                );
            case 'company':
                return <td style={style}>{job.company}</td>;
            case 'salary':
                return <td style={style}>{job.salary || 'N/A'}</td>;
            case 'posted_date':
                return <td style={style}>{formatDate(job.posted_date)}</td>;
            case 'created_at':
                return (
                    <td style={style}>
                        {formatDate(job.created_at)}
                        <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>{formatTime(job.created_at)}</div>
                    </td>
                );
            case 'reasoning':
                return (
                    <td style={style}>
                        <div style={{ fontSize: '0.9rem', lineHeight: '1.4' }}>{job.match_reasoning}</div>
                        {job.user_feedback_comment && (
                            <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(0,0,0,0.03)', borderRadius: '4px', fontSize: '0.85rem', borderLeft: '3px solid var(--accent)' }}>
                                <strong>Feedback:</strong> {job.user_feedback_comment}
                            </div>
                        )}
                    </td>
                );
            case 'actions':
                return (
                    <td style={style}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                                className="btn-icon"
                                onClick={() => handleThumbsUp(job)}
                                title="Good Match"
                                style={{ padding: '4px' }}
                            >
                                👍
                            </button>
                            <a
                                href={job.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn"
                                style={{
                                    padding: '0.25rem 0.75rem',
                                    fontSize: '0.8rem',
                                    backgroundColor: job.is_applied ? '#10b981' : 'var(--primary)',
                                    color: 'white'
                                }}
                                onClick={(e) => {
                                    e.preventDefault();
                                    updateJob(job.id, { is_applied: !job.is_applied });
                                }}
                            >
                                {job.is_applied ? 'Applied' : 'Apply'}
                            </a>
                        </div>
                    </td>
                );
            default:
                return <td style={style}></td>;
        }
    };

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem' }}>
                    <h1>Job Dashboard</h1>
                    <span style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>
                        {filteredJobs.length} {filteredJobs.length === 1 ? 'job' : 'jobs'} found
                    </span>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    {scraperStatus.state === 'RUNNING' && (
                        <span className="animate-pulse text-accent font-medium mr-2">
                            {scraperStatus.message || 'Scraper Running...'}
                        </span>
                    )}

                    {/* View Settings Dropdown */}
                    <div style={{ position: 'relative' }}>
                        <button className="btn" onClick={() => setShowSettings(!showSettings)}>
                            View Settings
                        </button>
                        {showSettings && (
                            <div style={{
                                position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem',
                                background: 'white', border: '1px solid #ddd', borderRadius: '8px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)', zIndex: 100, padding: '0.5rem',
                                minWidth: '150px'
                            }}>
                                <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Row Height</div>
                                {['compact', 'normal', 'comfortable'].map(h => (
                                    <div
                                        key={h}
                                        onClick={() => { setRowHeight(h); setShowSettings(false); }}
                                        style={{
                                            padding: '0.5rem', cursor: 'pointer',
                                            background: rowHeight === h ? 'var(--primary-light)' : 'transparent',
                                            borderRadius: '4px', textTransform: 'capitalize'
                                        }}
                                    >
                                        {h}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {selectedJobs.size > 0 && (
                        <button className="btn" style={{ backgroundColor: '#ef4444', color: 'white' }} onClick={deleteSelected}>
                            Delete ({selectedJobs.size})
                        </button>
                    )}
                    <button
                        className="btn btn-primary"
                        onClick={triggerRun}
                        disabled={scraperStatus.state === 'RUNNING'}
                    >
                        {scraperStatus.state === 'RUNNING' ? 'Running...' : 'Run Scraper'}
                    </button>
                </div>
            </div>

            <div className="card" style={{ padding: 0, overflowX: 'auto' }}>
                <table className="job-table" style={{ width: '100%', tableLayout: 'fixed' }}>
                    <thead>
                        <tr>
                            {columnOrder.map(colId => renderHeaderCell(colId))}
                        </tr>
                    </thead>
                    <tbody>
                        {sortedJobs.map(job => (
                            <tr key={job.id} className="job-row">
                                {columnOrder.map(colId => renderCell(job, colId))}
                            </tr>
                        ))}
                        {sortedJobs.length === 0 && (
                            <tr>
                                <td colSpan={columnOrder.length} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                                    No jobs found matching your filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
