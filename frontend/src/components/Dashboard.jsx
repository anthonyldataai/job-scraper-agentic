import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function Dashboard() {
    const [jobs, setJobs] = useState([]);
    const [sortBy, setSortBy] = useState('match_score');
    const [sortOrder, setSortOrder] = useState('desc');

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await axios.get(`${API_URL}/jobs`);
            setJobs(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSort = (field) => {
        if (sortBy === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortOrder('desc');
        }
    };

    const sortedJobs = [...jobs].sort((a, b) => {
        let aVal = a[sortBy];
        let bVal = b[sortBy];

        if (sortBy === 'posted_date') {
            aVal = aVal ? new Date(aVal) : new Date(0);
            bVal = bVal ? new Date(bVal) : new Date(0);
        }

        if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    const updateJob = async (id, data) => {
        try {
            await axios.patch(`${API_URL}/jobs/${id}`, data);
            fetchJobs();
        } catch (err) {
            console.error(err);
        }
    };

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

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1>Job Dashboard</h1>
                <button className="btn btn-primary" onClick={fetchJobs}>Refresh</button>
            </div>

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <table className="job-table">
                    <thead>
                        <tr>
                            <th onClick={() => handleSort('match_score')} style={{ width: '80px', textAlign: 'center' }}>Score</th>
                            <th onClick={() => handleSort('title')} style={{ width: '20%' }}>Title</th>
                            <th onClick={() => handleSort('company')} style={{ width: '15%' }}>Company</th>
                            <th onClick={() => handleSort('salary')} style={{ width: '12%' }}>Salary</th>
                            <th onClick={() => handleSort('posted_date')} style={{ width: '10%' }}>Posted</th>
                            <th style={{ width: '28%' }}>Reasoning</th>
                            <th style={{ width: '15%' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedJobs.map(job => (
                            <tr key={job.id}>
                                <td style={{ textAlign: 'center' }}>
                                    <div className={`score-badge ${job.match_score >= 80 ? 'score-high' :
                                            job.match_score >= 60 ? 'score-mid' :
                                                'score-low'
                                        }`}>
                                        {job.match_score}
                                    </div>
                                </td>
                                <td>
                                    <a href={job.link} target="_blank" rel="noopener noreferrer"
                                        style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}>
                                        {job.title}
                                    </a>
                                </td>
                                <td style={{ color: 'var(--text-secondary)' }}>{job.company}</td>
                                <td style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{job.salary || 'N/A'}</td>
                                <td style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{formatDate(job.posted_date)}</td>
                                <td>
                                    <div style={{
                                        fontSize: '0.85rem',
                                        lineHeight: '1.5',
                                        color: 'var(--text-secondary)',
                                        maxHeight: '80px',
                                        overflow: 'auto'
                                    }}>
                                        {job.match_reasoning || 'No reasoning provided'}
                                    </div>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        <button
                                            className={job.is_applied ? "btn btn-secondary" : "btn btn-primary"}
                                            onClick={() => updateJob(job.id, { is_applied: !job.is_applied })}
                                            style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                                        >
                                            {job.is_applied ? '✓ Applied' : 'Apply'}
                                        </button>
                                        <button
                                            className="btn btn-secondary"
                                            onClick={() => {
                                                const feedback = prompt('Enter feedback for this job:');
                                                if (feedback) updateJob(job.id, { user_feedback_comment: feedback });
                                            }}
                                            style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                                        >
                                            Feedback
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {jobs.length === 0 && (
                    <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No jobs found. Click "Trigger Scraper Run Now" in Configuration to start scraping.
                    </div>
                )}
            </div>
        </div>
    );
}
