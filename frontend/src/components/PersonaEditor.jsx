import React from 'react';

export default function PersonaEditor({ persona, onUpdate, onSave, saveStatus }) {
    if (!persona) return null;

    const updateField = (field, value) => {
        onUpdate({ ...persona, [field]: value });
    };

    const updateArray = (field, index, value) => {
        const newArray = [...persona[field]];
        newArray[index] = value;
        onUpdate({ ...persona, [field]: newArray });
    };

    const addArrayItem = (field) => {
        onUpdate({ ...persona, [field]: [...persona[field], ''] });
    };

    const removeArrayItem = (field, index) => {
        onUpdate({ ...persona, [field]: persona[field].filter((_, i) => i !== index) });
    };

    return (
        <div className="card mt-6">
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--primary)', fontFamily: 'var(--font-serif)' }}>
                Success Persona Editor
            </h2>
            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Edit the AI's understanding of your ideal job profile. This persona guides how jobs are evaluated and scored.
            </p>

            {/* Keywords */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Preferred Keywords</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    {persona.keywords?.map((keyword, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: 'var(--surface-alt)', padding: '0.25rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
                            <input
                                type="text"
                                value={keyword}
                                onChange={(e) => updateArray('keywords', idx, e.target.value)}
                                style={{ border: 'none', background: 'transparent', width: '120px', padding: '2px' }}
                            />
                            <button onClick={() => removeArrayItem('keywords', idx)} style={{ color: 'var(--error)', cursor: 'pointer', border: 'none', background: 'none', fontSize: '1.2rem' }}>×</button>
                        </div>
                    ))}
                </div>
                <button onClick={() => addArrayItem('keywords')} className="btn btn-secondary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>+ Add Keyword</button>
            </div>

            {/* Avoid Keywords */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Keywords to Avoid</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    {persona.avoid_keywords?.map((keyword, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: 'rgba(239, 68, 68, 0.1)', padding: '0.25rem 0.5rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                            <input
                                type="text"
                                value={keyword}
                                onChange={(e) => updateArray('avoid_keywords', idx, e.target.value)}
                                style={{ border: 'none', background: 'transparent', width: '120px', padding: '2px' }}
                            />
                            <button onClick={() => removeArrayItem('avoid_keywords', idx)} style={{ color: 'var(--error)', cursor: 'pointer', border: 'none', background: 'none', fontSize: '1.2rem' }}>×</button>
                        </div>
                    ))}
                </div>
                <button onClick={() => addArrayItem('avoid_keywords')} className="btn btn-secondary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>+ Add Keyword</button>
            </div>

            {/* Core Skills */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Core Skills</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    {persona.core_skills?.map((skill, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <input
                                type="text"
                                value={skill}
                                onChange={(e) => updateArray('core_skills', idx, e.target.value)}
                                style={{ flex: 1, padding: '0.5rem', borderRadius: '6px', border: '2px solid var(--border)' }}
                            />
                            <button onClick={() => removeArrayItem('core_skills', idx)} style={{ color: 'var(--error)', cursor: 'pointer', border: 'none', background: 'none', fontSize: '1.5rem' }}>×</button>
                        </div>
                    ))}
                </div>
                <button onClick={() => addArrayItem('core_skills')} className="btn btn-secondary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>+ Add Skill</button>
            </div>

            {/* Preferred Industries */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Preferred Industries</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    {persona.preferred_industries?.map((industry, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <input
                                type="text"
                                value={industry}
                                onChange={(e) => updateArray('preferred_industries', idx, e.target.value)}
                                style={{ flex: 1, padding: '0.5rem', borderRadius: '6px', border: '2px solid var(--border)' }}
                            />
                            <button onClick={() => removeArrayItem('preferred_industries', idx)} style={{ color: 'var(--error)', cursor: 'pointer', border: 'none', background: 'none', fontSize: '1.5rem' }}>×</button>
                        </div>
                    ))}
                </div>
                <button onClick={() => addArrayItem('preferred_industries')} className="btn btn-secondary" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>+ Add Industry</button>
            </div>

            {/* Experience Level */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Experience Level</label>
                <input
                    type="text"
                    value={persona.experience_level || ''}
                    onChange={(e) => updateField('experience_level', e.target.value)}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '2px solid var(--border)' }}
                    placeholder="e.g., Mid-Senior Level"
                />
            </div>

            {/* Cultural Fit */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Cultural Fit Description</label>
                <textarea
                    value={persona.cultural_fit || ''}
                    onChange={(e) => updateField('cultural_fit', e.target.value)}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '2px solid var(--border)', minHeight: '100px', fontFamily: 'inherit' }}
                    placeholder="Describe your ideal company culture..."
                />
            </div>

            {/* Scoring Rubric */}
            <div style={{ marginBottom: '1.5rem' }}>
                <label className="block mb-2 font-semibold text-primary">Scoring Rubric (Advanced)</label>
                <textarea
                    value={persona.scoring_rubric || ''}
                    onChange={(e) => updateField('scoring_rubric', e.target.value)}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '2px solid var(--border)', minHeight: '200px', fontFamily: 'monospace', fontSize: '0.85rem' }}
                    placeholder="Define how jobs should be scored..."
                />
            </div>

            {/* Save Button */}
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <button onClick={onSave} className="btn btn-primary">
                    Save Persona
                </button>
                {saveStatus === 'saving' && (
                    <span className="text-gray-500 text-sm font-medium">Saving...</span>
                )}
                {saveStatus === 'success' && (
                    <span className="text-success text-sm font-medium">✓ Persona saved successfully!</span>
                )}
                {saveStatus === 'error' && (
                    <span className="text-error text-sm font-medium">Error saving persona.</span>
                )}
            </div>
        </div>
    );
}
