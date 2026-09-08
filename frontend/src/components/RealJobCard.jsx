import React, { useState } from 'react';
import { ExternalLink, MapPin, DollarSign, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Building2 } from 'lucide-react';

export default function RealJobCard({ matchData }) {
  const [expanded, setExpanded] = useState(false);
  const job = matchData.real_job;
  const score = matchData.match_score;

  const getScoreClass = (s) => {
    if (s >= 80) return 'score-high';
    if (s >= 60) return 'score-medium';
    return 'score-low';
  };

  const getSourceBadgeStyle = (src) => {
    if (src === 'TopCV') {
      return { background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' };
    }
    return { background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.4)' };
  };

  const getValidApplyUrl = (j) => {
    if (!j || !j.source_url) return 'https://www.topcv.vn';
    const url = j.source_url;
    if (j.source === 'TopCV' && url.includes('/viec-lam/') && !url.includes('.html') && !url.includes('?') && !url.match(/-\d+$/)) {
      const titleLower = (j.title || '').toLowerCase();
      if (titleLower.includes('developer') || titleLower.includes('engineer') || titleLower.includes('python') || titleLower.includes('react') || titleLower.includes('backend') || titleLower.includes('ai') || titleLower.includes('fullstack') || titleLower.includes('devops')) {
        return 'https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?category_family=r257';
      }
      return `https://www.topcv.vn/tim-viec-lam?keyword=${encodeURIComponent(j.title || '')}`;
    }
    return url;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '16px', transition: 'var(--transition)' }}>
      
      {/* Header Row */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        
        {/* Company & Title Info */}
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
          <div style={{
            width: '48px', height: '48px', borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Building2 size={24} color="var(--accent-cyan)" />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{job.title}</h3>
              <span className="badge" style={getSourceBadgeStyle(job.source)}>
                {job.source}
              </span>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{job.company_name}</span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <MapPin size={14} color="var(--accent-primary)" /> {job.location}
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#34d399', fontWeight: 700 }}>
                <DollarSign size={14} /> {job.salary_text || 'Thỏa thuận'}
              </span>
            </p>
          </div>
        </div>

        {/* AI Score & Apply Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {score !== null && score !== undefined ? (
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-muted)' }}>Độ phù hợp AI</span>
              <span className={`score-pill ${getScoreClass(score)}`}>
                {score}% Match
              </span>
            </div>
          ) : (
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-muted)', fontStyle: 'italic' }}>Chưa quét CV</span>
              <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '2px', display: 'block' }}>
                Tải CV để khớp AI
              </span>
            </div>
          )}

          <a
            href={getValidApplyUrl(job)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-emerald"
            style={{ padding: '8px 16px', fontSize: '0.85rem', textDecoration: 'none' }}
          >
            Ứng tuyển trên {job.source} <ExternalLink size={14} />
          </a>
        </div>

      </div>

      {/* Skills Badges */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '14px' }}>
        {(job.required_skills || []).map((sk, idx) => (
          <span key={idx} style={{
            fontSize: '0.75rem', background: 'rgba(255,255,255,0.06)', padding: '4px 10px',
            borderRadius: '6px', border: '1px solid var(--border-color)', color: 'var(--text-secondary)'
          }}>
            {sk}
          </span>
        ))}
      </div>

      {/* Toggle Expand AI Reasoning */}
      <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => setExpanded(!expanded)}
          style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          {expanded ? 'Ẩn Phân tích Khớp nối AI' : 'Xem Lý do AI Đánh giá Khớp'}
        </button>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Kinh nghiệm: {job.experience_required || 'Không yêu cầu'}</span>
      </div>

      {/* Expanded Breakdown */}
      {expanded && (
        <div className="animate-fade-in" style={{ marginTop: '14px', background: 'rgba(0, 0, 0, 0.3)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '12px', borderRadius: '8px' }}>
              <h5 style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={14} /> Lý do Bạn Phù hợp
              </h5>
              <ul style={{ paddingLeft: '16px', fontSize: '0.8rem' }}>
                {(matchData.strengths_summary || []).map((st, i) => <li key={i}>{st}</li>)}
              </ul>
            </div>

            <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '12px', borderRadius: '8px' }}>
              <h5 style={{ fontSize: '0.8rem', color: '#f87171', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <AlertTriangle size={14} /> Điểm Cần Bổ sung
              </h5>
              <ul style={{ paddingLeft: '16px', fontSize: '0.8rem' }}>
                {(matchData.gaps_summary || []).map((gp, i) => <li key={i}>{gp}</li>)}
              </ul>
            </div>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            <b>Chi tiết JD:</b> {job.description_text}
          </p>
        </div>
      )}

    </div>
  );
}
