import React from 'react';
import { Briefcase, UserCheck, Sparkles, Layers, Globe } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <header className="glass-panel" style={{ marginBottom: '24px', padding: '16px 28px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)'
          }}>
            <Sparkles size={22} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
              ResumeScreening <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Động cơ Khớp nối AI 2 Giai đoạn & Tư vấn Lộ trình Career Gap
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', background: 'rgba(0, 0, 0, 0.3)', padding: '4px', borderRadius: '12px', gap: '4px' }}>
          <button
            onClick={() => setActiveTab('recruiter')}
            className={`btn ${activeTab === 'recruiter' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '8px', padding: '8px 16px', fontSize: '0.85rem' }}
          >
            <Briefcase size={16} />
            Không gian Tuyển dụng
          </button>
          
          <button
            onClick={() => setActiveTab('real-jobs')}
            className={`btn ${activeTab === 'real-jobs' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '8px', padding: '8px 16px', fontSize: '0.85rem' }}
          >
            <Globe size={16} color="var(--accent-cyan)" />
            Tìm Việc Thật (TopCV / ITViec)
          </button>

          <button
            onClick={() => setActiveTab('gap-advisor')}
            className={`btn ${activeTab === 'gap-advisor' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '8px', padding: '8px 16px', fontSize: '0.85rem' }}
          >
            <UserCheck size={16} />
            Tư vấn Khoảng trống CV
          </button>
        </div>

        {/* Model Engine Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.05)', padding: '6px 14px', borderRadius: '999px', border: '1px solid var(--border-color)' }}>
          <Layers size={14} color="var(--accent-cyan)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Gemini 1.5 Flash
          </span>
        </div>

      </div>
    </header>
  );
}
