import React from 'react';
import { X, CheckCircle2, AlertTriangle, Cpu, Code2, Briefcase, GraduationCap } from 'lucide-react';

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
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px'
    }}>
      <div className="glass-panel animate-fade-in" style={{
        width: '100%', maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto', padding: '32px',
        border: '1px solid var(--border-glow)'
      }}>
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>{candidate.candidate_name}</h2>
              <span className="score-pill score-high">Điểm Phù hợp: {candidate.overall_score}%</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              File CV: {candidate.candidate_file_name} {candidate.candidate_email && `| Email: ${candidate.candidate_email}`}
            </p>
          </div>

          <button onClick={onClose} className="btn btn-secondary" style={{ padding: '6px' }}>
            <X size={20} />
          </button>
        </div>

        {/* Breakdown Sub-scores with Candidate Details */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          
          {/* Skills Match Card */}
          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '18px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Code2 size={15} color="var(--accent-cyan)" /> Khớp Kỹ năng
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  {candidate.skills_sub_score}%
                </div>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, marginTop: '8px', borderTop: '1px dashed rgba(255,255,255,0.1)', paddingTop: '8px', lineHeight: '1.4' }}>
                <b>Kỹ năng:</b> {skillsText}
              </p>
            </div>
          </div>

          {/* Experience Match Card */}
          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '18px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Briefcase size={15} color="#a855f7" /> Phù hợp Kinh nghiệm
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#a855f7', fontFamily: 'var(--font-mono)' }}>
                  {candidate.experience_sub_score}%
                </div>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, marginTop: '8px', borderTop: '1px dashed rgba(255,255,255,0.1)', paddingTop: '8px', lineHeight: '1.4' }}>
                <b>Kinh nghiệm:</b> {expText}
              </p>
            </div>
          </div>

          {/* Education Match Card */}
          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '18px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <GraduationCap size={15} color="#10b981" /> Bằng cấp & Học vấn
                </span>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                  {candidate.education_sub_score}%
                </div>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, marginTop: '8px', borderTop: '1px dashed rgba(255,255,255,0.1)', paddingTop: '8px', lineHeight: '1.4' }}>
                <b>Bằng cấp:</b> {eduText}
              </p>
            </div>
          </div>

        </div>

        {/* Strengths vs Gaps */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
          
          {/* Key Strengths */}
          <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '18px', borderRadius: '14px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#34d399', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} /> Điểm mạnh Nổi bật
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
          <div style={{ background: 'rgba(244, 63, 94, 0.05)', padding: '18px', borderRadius: '14px', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#f87171', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={16} /> Điểm thiếu sót / Cần bổ bổ sung
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
        <div style={{ background: 'rgba(0,0,0,0.4)', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-cyan)' }}>
            <Cpu size={16} /> Phân tích Chi tiết từ Gemini AI
          </h4>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-secondary)', whitespace: 'pre-line' }}>
            {candidate.ai_reasoning || 'Đánh giá chi tiết được tạo tự động bởi mô hình Gemini AI 2 giai đoạn.'}
          </p>
        </div>

        {/* Footer Close */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
          <button onClick={onClose} className="btn btn-primary">Đóng Phân tích</button>
        </div>

      </div>
    </div>
  );
}
