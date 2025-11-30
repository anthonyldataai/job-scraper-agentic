import React from 'react';
import { LayoutDashboard, Settings, Terminal, PlusCircle } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
    const menuItems = [
        { id: 'dashboard', label: 'Job Dashboard', icon: LayoutDashboard },
        { id: 'logs', label: 'Agent Logs', icon: Terminal },
        { id: 'external', label: 'External Input', icon: PlusCircle },
        { id: 'config', label: 'Configuration', icon: Settings },
    ];

    return (
        <div className="sidebar">
            <div style={{ marginBottom: '2.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: 36, height: 36, background: 'var(--accent)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 10px rgba(212, 175, 55, 0.4)' }}>
                    <div style={{ width: 20, height: 20, background: 'var(--primary)', borderRadius: '50%' }}></div>
                </div>
                <h2 style={{ fontSize: '1.25rem', color: 'var(--surface)', fontFamily: 'var(--font-serif)', letterSpacing: '0.02em' }}>Agentic JobFlow</h2>
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <a
                            key={item.id}
                            href="#"
                            className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                            onClick={(e) => { e.preventDefault(); setActiveTab(item.id); }}
                        >
                            <Icon size={20} />
                            {item.label}
                        </a>
                    );
                })}
            </nav>

            <div style={{ marginTop: 'auto' }}>
                <div className="card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--surface)' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent)', fontSize: '0.9rem' }}>Status: Active</h4>
                    <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.8 }}>
                        Next run in 24 mins
                    </p>
                </div>
            </div>
        </div>
    );
}
