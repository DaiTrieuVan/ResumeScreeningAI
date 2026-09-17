/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useState } from 'react';
import { UserCheck, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Loader2, UploadCloud, Compass, Award, BarChart3, RotateCcw } from 'lucide-react';
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

    try {
      const res = await analyzeGap(jobTitle, jobDescription, cvFile);
      setResult(res);
    } catch (err) {
      setError('Phân tích thất bại: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const categoryLabels = {
    kinh_nghiem: 'Kinh nghiệm',
    ky_nang: 'Kỹ năng kỹ thuật',
    dinh_dang: 'Định dạng & Trình bày',
    thanh_tich: 'Thành tích & Tác động',
    muc_tieu: 'Mục tiêu & Sáng kiến'
  };

  return (
    <div className="advisor-page animate-fade-in" style={{ paddingBottom: '40px' }}>
      
      {/* Intro Hero */}
      <div className="advisor-hero" style={{ marginBottom: '24px' }}>
        <div className="advisor-hero__icon"><Compass size={24} /></div>
        <div>
          <span className="page-kicker">Trợ lý Đánh giá CV & Cố vấn Nghề nghiệp AI</span>
          <h2>Phân tích CV chuyên sâu & Xây dựng lộ trình cải thiện</h2>
          <p>So sánh CV với vị trí mục tiêu để chấm điểm, nhận diện điểm mạnh điểm yếu và đề xuất giải pháp tối ưu.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1.3fr' : '1fr', gap: '24px', alignItems: 'start' }}>
        
        {/* Input Form */}
        <div className="glass-panel advisor-form-card" style={{ padding: '24px' }}>
          <div className="panel-heading" style={{ marginBottom: '18px' }}>
            <div>
              <span className="section-eyebrow"><UserCheck size={15} /> Thông tin đầu vào</span>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Cho AI biết mục tiêu của bạn</h3>
            </div>
            {result && (
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setResult(null)}
                style={{ fontSize: '0.8rem', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <RotateCcw size={14} /> Thử CV khác
              </button>
            )}
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Vị trí mục tiêu <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(không bắt buộc)</span>
              </label>
              <input
                className="input-field"
                placeholder="Ví dụ: Java Web Backend Developer Intern"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Mô tả công việc mục tiêu <span style={{ color: 'var(--accent-rose)' }}>*</span>
              </label>
              <textarea
                className="textarea-field"
                rows="7"
                placeholder="Dán nội dung mô tả công việc và các yêu cầu của vị trí tuyển dụng vào đây..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', marginBottom: '6px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                CV của bạn (PDF)
              </label>
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

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ justifyContent: 'center', marginTop: '8px', padding: '12px' }}>
              {loading ? (
                <>
                  <Loader2 size={16} className="spin" /> Đang đánh giá chi tiết CV...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Đánh giá & Xây dựng lộ trình
                </>
              )}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '16px', color: '#b84250', fontSize: '0.85rem', background: '#fff0f1', padding: '12px', borderRadius: '8px', border: '1px solid #f0c7cb' }}>
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }} className="animate-fade-in">
            
            {/* 1. OVERALL SCORE BANNER CARD */}
            <div style={{
              background: 'linear-gradient(135deg, #06382b 0%, #0c4a39 100%)',
              borderRadius: '16px',
              padding: '24px',
              color: '#ffffff',
              boxShadow: '0 10px 25px -5px rgba(6, 56, 43, 0.4)',
              border: '1px solid #15634d'
            }}>
              <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', tracking: '1px', fontWeight: 700, opacity: 0.85, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '16px' }}>
                <Award size={16} color="#2dd4bf" /> TRỢ LÝ CV AI - KẾT QUẢ ĐÁNH GIÁ CV
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap' }}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '2px solid #2dd4bf',
                  borderRadius: '16px',
                  padding: '16px 28px',
                  minWidth: '130px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                    <span style={{ fontSize: '3rem', fontWeight: 800, color: '#2dd4bf', lineHeight: 1 }}>{result.overall_score || 7.5}</span>
                    <span style={{ fontSize: '1.1rem', color: '#94a3b8', fontWeight: 600 }}>/10</span>
                  </div>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff', marginTop: '4px' }}>
                    {result.score_label || 'Tốt'}
                  </span>
                </div>

                <div style={{ flex: 1, minWidth: '200px' }}>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '6px', color: '#ffffff' }}>Điểm đánh giá chung</h4>
                  <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5, margin: 0 }}>
                    Hồ sơ của bạn đạt mức xếp loại <b>{result.score_label || 'Tốt'}</b> so với yêu cầu công việc. Hãy xem chi tiết điểm từng danh mục và các khuyến nghị cải thiện bên dưới.
                  </p>
                </div>
              </div>
            </div>

            {/* 2. CATEGORY SCORES CARD */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart3 size={18} color="var(--accent-primary)" />
                Điểm theo danh mục
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {Object.entries(result.category_scores || { kinh_nghiem: 6.5, ky_nang: 8.0, dinh_dang: 6.0, thanh_tich: 7.0, muc_tieu: 6.5 }).map(([key, score]) => (
                  <div key={key}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{categoryLabels[key] || key}</span>
                      <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>{score}/10</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                      <div 
                        style={{ 
                          width: `${Math.min(100, Math.max(10, score * 10))}%`, 
                          height: '100%', 
                          background: score >= 8 ? 'linear-gradient(90deg, #087455, #2dd4bf)' : score >= 6 ? '#087455' : '#f59e0b',
                          borderRadius: '4px',
                          transition: 'width 0.6s ease-in-out'
                        }} 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. STRENGTHS & WEAKNESSES GRID */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              
              {/* STRENGTHS */}
              <div style={{ background: '#f0fdf7', padding: '18px', borderRadius: '14px', border: '1px solid #b7ebd9' }}>
                <h4 style={{ fontSize: '0.92rem', color: '#087455', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={18} color="#087455" /> Điểm mạnh
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {(result.strengths && result.strengths.length > 0 ? result.strengths : result.matched_skills).map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.83rem', color: '#164e3d', lineHeight: 1.45 }}>
                      <span style={{ color: '#087455', fontWeight: 700, marginTop: '1px' }}>✓</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* WEAKNESSES */}
              <div style={{ background: '#fffbeb', padding: '18px', borderRadius: '14px', border: '1px solid #fef3c7' }}>
                <h4 style={{ fontSize: '0.92rem', color: '#b45309', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={18} color="#b45309" /> Điểm yếu
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {(result.weaknesses && result.weaknesses.length > 0 ? result.weaknesses : result.missing_skills).map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.83rem', color: '#78350f', lineHeight: 1.45 }}>
                      <span style={{ color: '#b45309', fontWeight: 700, marginTop: '1px' }}>⚠️</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* 4. ACTIONABLE RECOMMENDATIONS */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} color="var(--accent-primary)" />
                Khuyến nghị cải thiện
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(result.suggested_action_items || []).map((action, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    background: '#f8fafc',
                    padding: '12px 16px',
                    borderRadius: '10px',
                    border: '1px solid #e2e8f0',
                    fontSize: '0.85rem',
                    lineHeight: 1.5
                  }}>
                    <div style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: '#06382b',
                      color: '#ffffff',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      marginTop: '1px'
                    }}>
                      {idx + 1}
                    </div>
                    <span style={{ color: 'var(--text-primary)' }}>{action}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 5. MATCHED VS MISSING SKILL BADGES & DETAILED OVERVIEW */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px', color: 'var(--text-primary)' }}>
                Chi tiết năng lực & Từ khóa kỹ thuật
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#087455', display: 'block', marginBottom: '6px' }}>Năng lực đã có trong CV:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {(result.matched_skills || []).map((s, idx) => (
                      <span key={idx} className="badge badge-shortlisted">{s}</span>
                    ))}
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#b84250', display: 'block', marginBottom: '6px' }}>Năng lực cần bổ sung thêm:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {(result.missing_skills || []).map((s, idx) => (
                      <span key={idx} className="badge badge-rejected">{s}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div style={{ 
                background: '#eef5f2', 
                padding: '16px', 
                borderRadius: '10px', 
                fontSize: '0.86rem', 
                color: 'var(--text-secondary)', 
                borderLeft: '4px solid var(--accent-primary)',
                lineHeight: 1.5
              }}>
                <b style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>Nhận xét chi tiết:</b> 
                {result.summary_explanation}
              </div>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}
