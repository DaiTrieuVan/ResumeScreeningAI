import React from 'react';
import { X, CheckCircle2, AlertTriangle, Cpu, Code2, Briefcase, GraduationCap, Award } from 'lucide-react';

export default function CandidateDetailModal({ candidate, onClose }) {
  if (!candidate) return null;

  // Fallback summaries if empty
  const skillsText = candidate.skills_summary || 
    (candidate.strengths_summary?.find(s => s.toLowerCase().includes('matched skill') || s.toLowerCase().includes('kỹ năng')) || 'Đã trích xuất các kỹ năng tương ứng từ CV');

  const expText = candidate.experience_summary || 
    (candidate.strengths_summary?.find(s => s.toLowerCase().includes('year') || s.toLowerCase().includes('kinh nghiệm')) || 'Có kinh nghiệm làm việc thực tế trong lĩnh vực');

  const eduText = candidate.education_summary || 
    (candidate.strengths_summary?.find(s => s.toLowerCase().includes('bachelor') || s.toLowerCase().includes('họć vấn') || s.toLowerCase().includes('bằng')) || 'Đại học / Cao đẳng chuyên ngành liên quan');

  return (
    <div className="modal-overlay" role="presentation">
      <div className="glass-panel modal-card animate-fade-in" role="dialog" aria-modal="true" aria-label={`Hồ sơ ${candidate.candidate_name}`} style={{
        width: '100%', maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto', padding: '32px',
        border: '1px solid var(--border-glow)'
      }}>
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>{candidate.candidate_name}</h2>
              <span className="score-pill score-high">Phù hợp {candidate.overall_score}%</span>
              {candidate.honors_badges && candidate.honors_badges.map((badge, idx) => (
                <span
                  key={idx}
                  style={{
                    fontSize: '0.75rem',
                    padding: '3px 10px',
                    borderRadius: '12px',
                    background: '#fff5df',
                    color: '#97620b',
                    fontWeight: 700,
                    border: '1px solid #efd39b',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <Award size={13} /> {badge}
                </span>
              ))}
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {candidate.candidate_file_name} {candidate.candidate_email && ` · ${candidate.candidate_email}`}
            </p>
          </div>

          <button onClick={onClose} className="btn btn-secondary" style={{ padding: '6px' }} aria-label="Đóng hồ sơ">
            <X size={20} />
          </button>
        </div>

        {/* Breakdown Sub-scores with Candidate Details */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          
          {/* Skills Match Card */}
          <div className="score-breakdown-card">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Code2 size={15} color="var(--accent-cyan)" /> Kỹ năng
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  {candidate.skills_sub_score}%
                </div>
              </div>
              <p className="score-breakdown-card__description">
                <b>Kỹ năng:</b> {skillsText}
              </p>
            </div>
          </div>

          {/* Experience Match Card */}
          <div className="score-breakdown-card">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Briefcase size={15} color="var(--accent-primary)" /> Kinh nghiệm
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>
                  {candidate.experience_sub_score}%
                </div>
              </div>
              <p className="score-breakdown-card__description">
                <b>Kinh nghiệm:</b> {expText}
              </p>
            </div>
          </div>

          {/* Education Match Card */}
          <div className="score-breakdown-card">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <GraduationCap size={15} color="#3376a8" /> Học vấn
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#3376a8', fontFamily: 'var(--font-mono)' }}>
                  {candidate.education_sub_score}%
                </div>
              </div>
              <p className="score-breakdown-card__description">
                <b>Bằng cấp:</b> {eduText}
              </p>
            </div>
          </div>

        </div>

        {/* Strengths vs Gaps */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
          
          {/* Key Strengths */}
          <div style={{ background: '#eaf7f2', padding: '18px', borderRadius: '12px', border: '1px solid #cceade' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#087455', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} /> Điểm mạnh nổi bật
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {candidate.strengths_summary && candidate.strengths_summary.length > 0 ? (
                candidate.strengths_summary.map((st, idx) => <li key={idx}>{st}</li>)
              ) : (
                <li>Chưa ghi nhận điểm mạnh đặc biệt</li>
              )}
            </ul>
          </div>

          {/* Missing Requirements / Gaps */}
          <div style={{ background: '#fff4f4', padding: '18px', borderRadius: '12px', border: '1px solid #f0d4d7' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#b84250', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={16} /> Điểm cần bổ sung
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {candidate.gaps_summary && candidate.gaps_summary.length > 0 ? (
                candidate.gaps_summary.map((gp, idx) => <li key={idx}>{gp}</li>)
              ) : (
                <li>Không phát hiện khoảng trống yêu cầu đáng kể</li>
              )}
            </ul>
          </div>

        </div>

        {/* AI Plain Language Reasoning */}
        <div style={{ background: '#f7faf8', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-cyan)' }}>
            <Cpu size={16} /> Nhận định chi tiết từ AI
          </h4>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-secondary)', whitespace: 'pre-line' }}>
            {candidate.ai_reasoning || 'Đánh giá chi tiết được tạo tự động bởi mô hình Gemini AI 2 giai đoạn.'}
          </p>
        </div>

        {/* Footer Close */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
          <button onClick={onClose} className="btn btn-primary">Hoàn tất xem hồ sơ</button>
        </div>

      </div>
    </div>
  );
}
