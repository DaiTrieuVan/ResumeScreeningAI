import React, { useState } from 'react';
import { UserCheck, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Loader2 } from 'lucide-react';
import { analyzeGap } from '../services/api';

export default function GapAdvisorView() {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [cvFile, setCvFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await analyzeGap(jobTitle, jobDescription, cvFile);
      setResult(res);
    } catch (err) {
      setError('Phân tích thất bại: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Intro Header */}
      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', textAlign: 'center' }}>
        <div style={{
          width: '50px', height: '50px', borderRadius: '14px', background: 'var(--accent-gradient)',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '12px'
        }}>
          <UserCheck size={26} color="#fff" />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Tư vấn Lộ trình & Khoảng trống CV (Career Gap Advisor)</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '600px', margin: '8px auto 0' }}>
          So sánh CV của bạn với Mô tả Công việc (JD) mục tiêu để khám phá độ khớp kỹ năng, điểm thiếu sót và bước đi cụ thể để nâng cao hồ sơ ứng tuyển.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1.2fr' : '1fr', gap: '24px' }}>
        
        {/* Input Form */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Tên Vị trí Mục tiêu (Tùy chọn)</label>
              <input
                className="input-field"
                placeholder="VD: Kỹ sư Hệ thống AI Senior"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Mô tả Công việc Mục tiêu (JD) *</label>
              <textarea
                className="textarea-field"
                rows="6"
                placeholder="Dán toàn bộ văn bản yêu cầu công việc hoặc mô tả JD vào đây..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Tải lên CV của bạn (Định dạng PDF)</label>
              <input
                type="file"
                accept=".pdf"
                className="input-field"
                onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ justifyContent: 'center', marginTop: '8px' }}>
              {loading ? (
                <>
                  <Loader2 size={16} className="spin" /> Đang phân tích độ khớp nối...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Phân tích Khoảng trống CV
                </>
              )}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '16px', color: '#f87171', fontSize: '0.85rem', background: 'rgba(244,63,94,0.1)', padding: '10px', borderRadius: '8px' }}>
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        {result && (
          <div className="glass-panel animate-fade-in" style={{ padding: '28px', border: '1px solid var(--border-glow)' }}>
            
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles color="var(--accent-cyan)" size={20} />
              Kết quả Phân tích Khoảng trống CV
            </h3>

            {/* Matched vs Missing */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
              
              <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <h4 style={{ fontSize: '0.85rem', color: '#34d399', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} /> Kỹ năng Phù hợp & Điểm mạnh
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {result.matched_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-shortlisted">{s}</span>
                  ))}
                </div>
              </div>

              <div style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
                <h4 style={{ fontSize: '0.85rem', color: '#f87171', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={16} /> Kỹ năng & Yêu cầu Còn thiếu
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {result.missing_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-rejected">{s}</span>
                  ))}
                </div>
              </div>

            </div>

            {/* Action Items */}
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px', color: 'var(--accent-cyan)' }}>
                Khuyến nghị Hành động Nâng cấp CV:
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {result.suggested_action_items.map((item, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '10px', background: 'rgba(0,0,0,0.3)',
                    padding: '12px', borderRadius: '8px', fontSize: '0.85rem'
                  }}>
                    <ArrowRight size={16} color="var(--accent-primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanation */}
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '14px', borderRadius: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <b>Tóm tắt:</b> {result.summary_explanation}
            </div>

          </div>
        )}

      </div>

    </div>
  );
}
