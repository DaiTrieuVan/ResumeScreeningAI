/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useState } from 'react';
import { UserCheck, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Loader2, UploadCloud, Compass } from 'lucide-react';
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
    <div className="advisor-page animate-fade-in">
      
      {/* Intro Header */}
      <div className="advisor-hero">
        <div className="advisor-hero__icon"><Compass size={24} /></div>
        <div>
          <span className="page-kicker">Cố vấn nghề nghiệp cùng AI</span>
          <h2>Biến khoảng trống kỹ năng thành lộ trình phát triển</h2>
          <p>So sánh CV với vị trí mục tiêu để biết bạn đã sẵn sàng đến đâu và nên ưu tiên cải thiện điều gì tiếp theo.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1.2fr' : '1fr', gap: '24px' }}>
        
        {/* Input Form */}
        <div className="glass-panel advisor-form-card">
          <div className="panel-heading">
            <div>
              <span className="section-eyebrow"><UserCheck size={15} /> Thông tin phân tích</span>
              <h3>Cho AI biết mục tiêu của bạn</h3>
            </div>
          </div>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Vị trí mục tiêu <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(không bắt buộc)</span></label>
              <input
                className="input-field"
                placeholder="Ví dụ: Kỹ sư hệ thống AI cấp cao"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>Mô tả công việc mục tiêu <span style={{ color: 'var(--accent-rose)' }}>*</span></label>
              <textarea
                className="textarea-field"
                rows="6"
                placeholder="Dán nội dung mô tả công việc và các yêu cầu của vị trí vào đây..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>CV của bạn</label>
              <input
                type="file"
                accept=".pdf"
                id="advisor-cv-file"
                style={{ display: 'none' }}
                onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
              />
              <label htmlFor="advisor-cv-file" className="advisor-file-picker">
                <UploadCloud size={20} />
                <span>{cvFile ? cvFile.name : 'Chọn CV định dạng PDF'}</span>
                <small>{cvFile ? 'Bấm để chọn tệp khác' : 'Tệp tối đa 10 MB'}</small>
              </label>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ justifyContent: 'center', marginTop: '8px' }}>
              {loading ? (
                <>
                  <Loader2 size={16} className="spin" /> Đang phân tích hồ sơ...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Xây dựng lộ trình cho tôi
                </>
              )}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '16px', color: '#b84250', fontSize: '0.85rem', background: '#fff0f1', padding: '10px', borderRadius: '8px', border: '1px solid #f0c7cb' }}>
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        {result && (
          <div className="glass-panel advisor-result animate-fade-in" style={{ padding: '28px', border: '1px solid var(--border-glow)' }}>
            
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles color="var(--accent-cyan)" size={20} />
              Lộ trình dành cho bạn
            </h3>

            {/* Matched vs Missing */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
              
              <div style={{ background: '#eaf7f2', padding: '16px', borderRadius: '10px', border: '1px solid #cceade' }}>
                <h4 style={{ fontSize: '0.85rem', color: '#087455', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} /> Điểm mạnh hiện có
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {result.matched_skills.map((s, idx) => (
                    <span key={idx} className="badge badge-shortlisted">{s}</span>
                  ))}
                </div>
              </div>

              <div style={{ background: '#fff4f4', padding: '16px', borderRadius: '10px', border: '1px solid #f0d4d7' }}>
                <h4 style={{ fontSize: '0.85rem', color: '#b84250', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={16} /> Năng lực cần bổ sung
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
                Những việc nên ưu tiên tiếp theo
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {result.suggested_action_items.map((item, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '10px', background: '#f7faf8',
                    padding: '12px', borderRadius: '8px', fontSize: '0.85rem'
                  }}>
                    <ArrowRight size={16} color="var(--accent-primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanation */}
            <div style={{ background: '#eef5f2', padding: '14px', borderRadius: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)', borderLeft: '3px solid var(--accent-primary)' }}>
              <b style={{ color: 'var(--text-primary)' }}>Nhận định tổng quan:</b> {result.summary_explanation}
            </div>

          </div>
        )}

      </div>

    </div>
  );
}
