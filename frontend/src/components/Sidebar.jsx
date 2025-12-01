import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Settings, Terminal, PlusCircle, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [isPinned, setIsPinned] = useState(true);

    // Load sidebar state from localStorage
    useEffect(() => {
        const savedState = localStorage.getItem('sidebar_state');
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                if (parsed.isPinned !== undefined) setIsPinned(parsed.isPinned);
                if (parsed.isCollapsed !== undefined) setIsCollapsed(parsed.isCollapsed);
            } catch (e) {
                console.error("Failed to load sidebar state", e);
            }
        }
    }, []);

    // Save sidebar state to localStorage
    useEffect(() => {
        localStorage.setItem('sidebar_state', JSON.stringify({ isPinned, isCollapsed }));
    }, [isPinned, isCollapsed]);

    const menuItems = [
        { id: 'dashboard', label: 'Job Dashboard', icon: LayoutDashboard },
        { id: 'logs', label: 'Agent Logs', icon: Terminal },
        { id: 'external', label: 'External Input', icon: PlusCircle },
        { id: 'config', label: 'Configuration', icon: Settings },
    ];

    const toggleCollapse = () => {
        setIsCollapsed(!isCollapsed);
    };

    const togglePin = () => {
        setIsPinned(!isPinned);
        if (isPinned) {
            setIsCollapsed(true);
        }
    };

    return (
        <>
            <div
                className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}
                style={{
                    width: isCollapsed ? '60px' : '250px',
                    transition: 'width 0.3s ease'
                }}
            >
                {/* Toggle Button */}
                <button
                    onClick={toggleCollapse}
                    style={{
                        position: 'absolute',
                        right: '-12px',
                        top: '20px',
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: 'var(--primary)',
                        border: '2px solid var(--surface)',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        zIndex: 1000,
                        padding: 0
                    }}
                    title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                </button>

                {/* Logo/Title */}
                <div style={{
                    marginBottom: '2.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: 36,
                        height: 36,
                        background: 'var(--accent)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 0 10px rgba(212, 175, 55, 0.4)',
                        flexShrink: 0
                    }}>
                        <div style={{ width: 20, height: 20, background: 'var(--primary)', borderRadius: '50%' }}></div>
                    </div>
                    {!isCollapsed && (
                        <h2 style={{
                            fontSize: '1.25rem',
                            color: 'var(--surface)',
                            fontFamily: 'var(--font-serif)',
                            letterSpacing: '0.02em',
                            whiteSpace: 'nowrap'
                        }}>
                            Agentic JobFlow
                        </h2>
                    )}
                </div>

                {/* Navigation */}
                <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <a
                                key={item.id}
                                href="#"
                                className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                                onClick={(e) => { e.preventDefault(); setActiveTab(item.id); }}
                                style={{
                                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                                    padding: isCollapsed ? '0.75rem' : '0.75rem 1rem'
                                }}
                                title={isCollapsed ? item.label : ''}
                            >
                                <Icon size={20} />
                                {!isCollapsed && item.label}
                            </a>
                        );
                    })}
                </nav>

                {/* Pin/Unpin Button */}
                {!isCollapsed && (
                    <div style={{ marginTop: '1rem', padding: '0 1rem' }}>
                        <button
                            onClick={togglePin}
                            style={{
                                width: '100%',
                                padding: '0.5rem',
                                background: isPinned ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255,255,255,0.05)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '6px',
                                color: 'var(--surface)',
                                fontSize: '0.85rem',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            {isPinned ? '📌 Pinned' : '📍 Auto-hide'}
                        </button>
                    </div>
                )}

                {/* Status Card */}
                {!isCollapsed && (
                    <div style={{ marginTop: 'auto' }}>
                        <div className="card" style={{
                            padding: '1rem',
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            color: 'var(--surface)'
                        }}>
                            <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent)', fontSize: '0.9rem' }}>
                                Status: Active
                            </h4>
                            <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.8 }}>
                                Connected to Agent Swarm
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Overlay for unpinned sidebar */}
            {!isPinned && !isCollapsed && (
                <div
                    onClick={() => setIsCollapsed(true)}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.3)',
                        zIndex: 999
                    }}
                />
            )}
        </>
    );
}
