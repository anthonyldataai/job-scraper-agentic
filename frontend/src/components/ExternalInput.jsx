import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function ExternalInput() {
    const [url, setUrl] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!url) return;

        try {
            await axios.post(`${API_URL}/jobs/external`, { url });
            alert("Job added! The agents will process it shortly.");
            setUrl("");
        } catch (err) {
            alert("Error adding job");
        }
    };

    return (
        <div className="animate-fade-in" style={{ maxWidth: '600px' }}>
            <h1>Add External Job</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Found a job manually? Add the link here and let the AI analyze and score it for you.</p>

            <div className="card" style={{ marginTop: '1rem' }}>
                <form onSubmit={handleSubmit}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Job URL</label>
                    <input
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://linkedin.com/jobs/..."
                        style={{ marginBottom: '1rem' }}
                    />
                    <button type="submit" className="btn btn-primary">Add to Pipeline</button>
                </form>
            </div>
        </div>
    );
}
