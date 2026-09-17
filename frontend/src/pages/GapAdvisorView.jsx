/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useState } from 'react';
import { 
  UserCheck, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2, 
  UploadCloud, 
  Compass, 
  RotateCcw, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  FileText,
  SpellCheck,
  Tag,
  MessageSquare
} from 'lucide-react';
import { analyzeGap } from '../services/api';

export default function GapAdvisorView() {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [cvFile, setCvFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Expandable sections state
  const [expandedCategories, setExpandedCategories] = useState({
    kinh_nghiem: true,
    ky_nang: true,
    dinh_dang: false,
    thanh_tich: false,
    muc_tieu: false
  });
  const [showInputSummary, setShowInputSummary] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await analyzeGap(jobTitle, jobDescription, cvFile);
      setResult(res);
      // Auto open first 2 categories
      setExpandedCategories({
        kinh_nghiem: true,
        ky_nang: true,
        dinh_dang: false,
        thanh_tich: false,
        muc_tieu: false
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

  const toggleCategory = (key) => {
    setExpandedCategories(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const allCategoriesExpanded = Object.values(expandedCategories).every(Boolean);

  const toggleExpandAllCategories = () => {
    const nextState = !allCategoriesExpanded;
    setExpandedCategories({
      kinh_nghiem: nextState,
      ky_nang: nextState,
      dinh_dang: nextState,
      thanh_tich: nextState,
      muc_tieu: nextState
    });
  };

  const handleCopyReport = () => {
    if (!result) return;
    const textLines = [
      `=== BÁO CÁO ĐÁNH GIÁ CV: ${jobTitle || 'Vị trí mục tiêu'} ===`,
      `Điểm tổng thể: ${result.overall_score}/10 (${result.score_label})`,
      `\n--- ĐIỂM THEO DANH MỤC ---`,
      ...Object.entries(result.category_scores || {}).map(([k, v]) => `- ${categoryLabels[k] || k}: ${v}/10`),
      `\n--- ĐIỂM MẠNH ---`,
      ...(result.strengths || []).map(s => `✓ ${s}`),
      `\n--- ĐIỂM YẾU ---`,
      ...(result.weaknesses || []).map(w => `⚠️ ${w}`),
      `\n--- KHUYẾN NGHỊ CẢI THIỆN ---`,
      ...(result.suggested_action_items || []).map((a, i) => `${i + 1}. ${a}`),
      `\n--- NHẬN XÉT CHI TIẾT ---`,
      result.summary_explanation || ''
    ];
    navigator.clipboard.writeText(textLines.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="advisor-page animate-fade-in" style={{ paddingBottom: '50px' }}>
      
      {/* ============================================================ */}
      {/* 1. INPUT FORM VIEW (When result is null) */}
      {/* ============================================================ */}
      {!result ? (
        <div style={{ maxWidth: '820px', margin: '0 auto' }}>
          
          {/* Hero Header */}
          <div className="advisor-hero" style={{ marginBottom: '28px', textAlign: 'left' }}>
            <div className="advisor-hero__icon"><Compass size={26} /></div>
            <div>
              <span className="page-kicker">Trợ lý Đánh giá CV & Cố vấn Nghề nghiệp AI</span>
              <h2>Biến khoảng trống kỹ năng thành lộ trình phát triển</h2>
              <p>So sánh CV với vị trí mục tiêu để chấm điểm, nhận diện điểm mạnh điểm yếu và đề xuất giải pháp tối ưu.</p>
            </div>
          </div>

          {/* Form Card */}
          <div className="glass-panel" style={{ padding: '32px', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)' }}>
            <div className="panel-heading" style={{ marginBottom: '22px' }}>
              <div>
                <span className="section-eyebrow"><UserCheck size={15} /> THÔNG TIN ĐẦU VÀO</span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '4px' }}>Cho AI biết mục tiêu của bạn</h3>
              </div>
            </div>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Vị trí mục tiêu <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(không bắt buộc)</span>
                </label>
                <input
                  className="input-field"
                  placeholder="Ví dụ: Java Web Backend Developer Intern"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  style={{ fontSize: '0.92rem', padding: '12px 14px' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Mô tả công việc mục tiêu <span style={{ color: 'var(--accent-rose)' }}>*</span>
                </label>
                <textarea
                  className="textarea-field"
                  rows="8"
                  placeholder="Dán nội dung mô tả công việc (JD) và các yêu cầu của vị trí tuyển dụng vào đây..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  required
                  style={{ fontSize: '0.9rem', lineHeight: 1.6 }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  CV của bạn (PDF)
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  id="advisor-cv-file"
                  style={{ display: 'none' }}
                  onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
                />
                <label htmlFor="advisor-cv-file" className="advisor-file-picker" style={{ padding: '24px 20px', cursor: 'pointer' }}>
                  <UploadCloud size={28} color="var(--accent-primary)" />
                  <span style={{ fontSize: '0.95rem', fontWeight: 600 }}>{cvFile ? cvFile.name : 'Chọn CV định dạng PDF'}</span>
                  <small>{cvFile ? 'Bấm để đổi tệp khác' : 'Tệp tối đa 10 MB'}</small>
                </label>
              </div>

              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={loading} 
                style={{ justifyContent: 'center', marginTop: '10px', padding: '14px 24px', fontSize: '0.98rem', fontWeight: 700 }}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="spin" /> Đang phân tích chi tiết CV theo chuẩn VietResume...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} /> Đánh giá & Xây dựng lộ trình
                  </>
                )}
              </button>
            </form>

            {error && (
              <div style={{ marginTop: '18px', color: '#991b1b', fontSize: '0.88rem', background: '#fef2f2', padding: '14px', borderRadius: '10px', border: '1px solid #fecaca' }}>
                {error}
              </div>
            )}
          </div>
        </div>
      ) : (
        
        /* ============================================================ */
        /* 2. FULL-WIDTH VIETRESUME-STYLE REPORT DASHBOARD              */
        /* ============================================================ */
        <div style={{ maxWidth: '980px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '22px' }} className="animate-fade-in">
          
          {/* 2.1 SUB-HEADER BANNER (Matching VietResume dark header) */}
          <div style={{
            background: '#112d25',
            borderRadius: '18px',
            padding: '20px 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '14px',
            color: '#ffffff',
            boxShadow: '0 10px 30px rgba(17, 45, 37, 0.25)'
          }}>
            <div>
              <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#2dd4bf', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <Sparkles size={15} /> TRỢ LÝ CV AI
              </div>
              <h2 style={{ fontSize: '1.45rem', fontWeight: 700, margin: 0, color: '#ffffff' }}>Kết quả đánh giá CV</h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                type="button"
                onClick={() => setShowInputSummary(!showInputSummary)}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: '#ffffff',
                  borderRadius: '9999px',
                  padding: '8px 16px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease'
                }}
              >
                <FileText size={14} /> {showInputSummary ? 'Ẩn thông tin JD' : 'Xem thông tin JD'}
              </button>

              <button
                type="button"
                onClick={() => setResult(null)}
                style={{
                  background: 'rgba(255, 255, 255, 0.12)',
                  border: '1px solid rgba(255, 255, 255, 0.28)',
                  color: '#ffffff',
                  borderRadius: '9999px',
                  padding: '8px 18px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease'
                }}
              >
                <RotateCcw size={14} /> Thử CV khác
              </button>
            </div>
          </div>

          {/* 2.1.1 COLLAPSIBLE INPUT SUMMARY (Optional) */}
          {showInputSummary && (
            <div className="glass-panel animate-fade-in" style={{ padding: '20px 26px', borderRadius: '16px', border: '1px solid #dfe7e3' }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Vị trí mục tiêu: <span style={{ color: 'var(--accent-primary-dark)' }}>{jobTitle || 'Không ghi rõ'}</span>
              </h4>
              <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', maxHeight: '140px', overflowY: 'auto', background: '#f8faf9', padding: '12px 14px', borderRadius: '8px', border: '1px solid #e5eae7', whiteSpace: 'pre-line', lineHeight: 1.5 }}>
                {jobDescription}
              </div>
            </div>
          )}

          {/* 2.2 OVERALL SCORE HERO CARD (Matching VietResume dark green card) */}
          <div style={{
            background: '#112d25',
            borderRadius: '18px',
            padding: '28px 32px',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '28px',
            boxShadow: '0 10px 30px rgba(17, 45, 37, 0.25)',
            border: '1px solid rgba(45, 212, 191, 0.2)'
          }}>
            {/* Big Circular Score Badge */}
            <div style={{
              width: '98px',
              height: '98px',
              borderRadius: '50%',
              border: '3.5px solid #2dd4bf',
              background: 'rgba(255, 255, 255, 0.05)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <span style={{ fontSize: '2.5rem', fontWeight: 800, color: '#2dd4bf', lineHeight: 1 }}>{result.overall_score || 7.5}</span>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600, marginTop: '2px' }}>/10</span>
            </div>

            {/* Score Text */}
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '2.1rem', fontWeight: 800, color: '#ffffff', lineHeight: 1.1 }}>{result.score_label || 'Tốt'}</div>
              <div style={{ fontSize: '0.95rem', color: '#cbd5e1', marginTop: '4px' }}>Điểm đánh giá chung</div>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '6px', lineHeight: 1.4 }}>
                Hồ sơ đạt mức độ tương thích cao với yêu cầu tuyển dụng. Xem chi tiết các hạng mục bên dưới để hoàn thiện CV tốt hơn.
              </div>
            </div>
          </div>

          {/* 2.3 CATEGORY SCORES WITH EXPANDABLE BREAKDOWN */}
          <div className="glass-panel" style={{ padding: '26px 30px', borderRadius: '18px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '22px', flexWrap: 'wrap', gap: '10px' }}>
              <h3 style={{ fontSize: '1.18rem', fontWeight: 700, margin: 0, color: '#16211d' }}>
                Điểm theo danh mục
              </h3>
              <button
                type="button"
                onClick={toggleExpandAllCategories}
                style={{
                  background: '#f1f5f9',
                  border: '1px solid #cbd5e1',
                  padding: '6px 14px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#334155',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {allCategoriesExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {allCategoriesExpanded ? 'Thu gọn chi tiết' : 'Mở rộng chi tiết'}
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '22px 32px' }}>
              {Object.entries(result.category_scores || { kinh_nghiem: 6.5, ky_nang: 8.0, dinh_dang: 5.5, thanh_tich: 7.0, muc_tieu: 6.5 }).map(([key, score]) => {
                const isExpanded = expandedCategories[key];
                const detailText = (result.category_details && result.category_details[key]) || 
                  (key === 'kinh_nghiem' ? 'Kinh nghiệm dự án cần nêu rõ vai trò cá nhân và bài học kỹ thuật khi khắc phục sự cố.' :
                   key === 'ky_nang' ? 'Kỹ năng công nghệ khá vững, cần bổ sung thêm các từ khóa chuyên sâu mà JD yêu cầu.' :
                   key === 'dinh_dang' ? 'Cần rà soát khoảng trắng dấu câu và chuẩn hóa viết hoa đúng tên công nghệ.' :
                   key === 'thanh_tich' ? 'Nên lượng hóa cụ thể hơn với các chỉ số đo lường như % tối ưu, latency, số người dùng.' :
                   'Mục tiêu cần hướng đến đóng góp cụ thể cho sản phẩm của doanh nghiệp.');

                return (
                  <div 
                    key={key} 
                    style={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: '8px',
                      background: isExpanded ? '#fafcfb' : 'transparent',
                      padding: isExpanded ? '12px 14px' : '4px 0',
                      borderRadius: '12px',
                      border: isExpanded ? '1px solid #e6eeea' : '1px solid transparent',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div 
                      onClick={() => toggleCategory(key)}
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', userSelect: 'none' }}
                    >
                      <span style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {categoryLabels[key] || key}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--accent-primary-dark)' }}>
                          {score}/10
                        </span>
                        {isExpanded ? <ChevronUp size={14} color="#8a9892" /> : <ChevronDown size={14} color="#8a9892" />}
                      </div>
                    </div>

                    {/* Sleek Progress Bar */}
                    <div 
                      onClick={() => toggleCategory(key)}
                      style={{ width: '100%', height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', cursor: 'pointer' }}
                    >
                      <div 
                        style={{ 
                          width: `${Math.min(100, Math.max(10, score * 10))}%`, 
                          height: '100%', 
                          background: score >= 8 ? 'linear-gradient(90deg, #087455, #10b981)' : score >= 6 ? '#087455' : '#f59e0b',
                          borderRadius: '4px',
                          transition: 'width 0.6s ease-in-out'
                        }} 
                      />
                    </div>

                    {/* Expandable Category Detail Drawer */}
                    {isExpanded && (
                      <div className="animate-fade-in" style={{ 
                        marginTop: '6px', 
                        padding: '10px 12px', 
                        background: '#ffffff', 
                        borderRadius: '8px', 
                        border: '1px solid #dbe6e0',
                        fontSize: '0.83rem',
                        color: 'var(--text-secondary)',
                        lineHeight: 1.5
                      }}>
                        <div style={{ fontWeight: 600, color: 'var(--accent-primary-dark)', marginBottom: '3px' }}>
                          💡 Đánh giá chi tiết:
                        </div>
                        {detailText}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 2.4 STRENGTHS & WEAKNESSES GRID (Matching VietResume screenshot 4) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '22px' }}>
            
            {/* STRENGTHS CARD */}
            <div className="glass-panel" style={{ padding: '24px', borderRadius: '18px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '18px', color: '#16211d', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={20} color="#087455" /> Điểm mạnh
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {(result.strengths && result.strengths.length > 0 ? result.strengths : result.matched_skills).map((item, idx) => (
                  <div 
                    key={idx} 
                    style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px', 
                      background: '#f0fdf7', 
                      padding: '14px 16px', 
                      borderRadius: '12px', 
                      border: '1px solid #b7ebd9',
                      fontSize: '0.87rem', 
                      color: '#164e3d', 
                      lineHeight: 1.55 
                    }}
                  >
                    <span style={{ 
                      color: '#087455', 
                      fontWeight: 800, 
                      fontSize: '1rem', 
                      marginTop: '-1px',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: '#d1fae5',
                      flexShrink: 0
                    }}>
                      ✓
                    </span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* WEAKNESSES CARD */}
            <div className="glass-panel" style={{ padding: '24px', borderRadius: '18px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '18px', color: '#16211d', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={20} color="#b45309" /> Điểm yếu
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {(result.weaknesses && result.weaknesses.length > 0 ? result.weaknesses : result.missing_skills).map((item, idx) => (
                  <div 
                    key={idx} 
                    style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '12px', 
                      background: '#fffbeb', 
                      padding: '14px 16px', 
                      borderRadius: '12px', 
                      border: '1px solid #fef3c7',
                      fontSize: '0.87rem', 
                      color: '#78350f', 
                      lineHeight: 1.55 
                    }}
                  >
                    <span style={{ 
                      color: '#b45309', 
                      fontWeight: 800, 
                      fontSize: '0.9rem', 
                      marginTop: '-1px',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: '#fef3c7',
                      flexShrink: 0
                    }}>
                      ⚠️
                    </span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* 2.5 RECOMMENDATIONS (Matching VietResume screenshot 4) */}
          <div className="glass-panel" style={{ padding: '26px 30px', borderRadius: '18px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <h3 style={{ fontSize: '1.18rem', fontWeight: 700, marginBottom: '20px', color: '#16211d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} color="var(--accent-primary)" /> Khuyến nghị cải thiện
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {(result.suggested_action_items || []).map((action, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                  background: '#f8fafc',
                  padding: '14px 18px',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0',
                  fontSize: '0.88rem',
                  lineHeight: 1.55
                }}>
                  <div style={{
                    width: '26px',
                    height: '26px',
                    borderRadius: '50%',
                    background: '#112d25',
                    color: '#ffffff',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '2px'
                  }}>
                    {idx + 1}
                  </div>
                  <span style={{ color: '#1e293b' }}>{action}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 2.6 SPELLING & TECH TERM CHECKER (Soát lỗi chính tả & Định dạng) */}
          {result.spelling_and_format_errors && result.spelling_and_format_errors.length > 0 && (
            <div className="glass-panel" style={{ padding: '24px 28px', borderRadius: '18px', border: '1px solid #fecaca', background: '#fffcfc' }}>
              <h3 style={{ fontSize: '1.1rem', color: '#991b1b', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <SpellCheck size={20} color="#dc2626" />
                Soát lỗi chính tả & Chuẩn hóa thuật ngữ kỹ thuật
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {result.spelling_and_format_errors.map((errItem, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    background: '#ffffff',
                    padding: '12px 16px',
                    borderRadius: '10px',
                    border: '1px solid #fee2e2',
                    fontSize: '0.86rem',
                    color: '#7f1d1d'
                  }}>
                    <span style={{ fontWeight: 800, color: '#dc2626', fontSize: '1.1rem' }}>•</span>
                    <span>{errItem}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2.7 TECHNICAL KEYWORDS & MATCHED SKILLS */}
          <div className="glass-panel" style={{ padding: '24px 28px', borderRadius: '18px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Tag size={19} color="var(--accent-primary)" />
              Chi tiết năng lực & Từ khóa kỹ thuật
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#087455', display: 'block', marginBottom: '8px' }}>
                  Năng lực đã có trong CV:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {(result.matched_skills || []).map((s, idx) => (
                    <span key={idx} className="badge badge-shortlisted" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#b84250', display: 'block', marginBottom: '8px' }}>
                  Năng lực cần bổ sung thêm theo yêu cầu JD:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {(result.missing_skills || []).map((s, idx) => (
                    <span key={idx} className="badge badge-rejected" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 2.8 DETAILED EXECUTIVE SUMMARY */}
          <div className="glass-panel" style={{ padding: '24px 28px', borderRadius: '18px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MessageSquare size={19} color="var(--accent-primary)" />
              Nhận xét chi tiết từ Trợ lý AI (VP of Engineering)
            </h3>
            <div style={{ 
              background: '#f8faf9', 
              padding: '18px 22px', 
              borderRadius: '12px', 
              fontSize: '0.88rem', 
              color: 'var(--text-secondary)', 
              borderLeft: '4px solid var(--accent-primary)',
              lineHeight: 1.65
            }}>
              {result.summary_explanation}
            </div>
          </div>

          {/* 2.9 BOTTOM ACTION BAR */}
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '14px', marginTop: '10px', flexWrap: 'wrap' }}>
            <button 
              type="button" 
              onClick={() => setResult(null)} 
              className="btn btn-primary" 
              style={{ padding: '12px 24px', fontSize: '0.9rem', fontWeight: 700 }}
            >
              <RotateCcw size={16} /> Thử đánh giá CV khác
            </button>
            <button 
              type="button" 
              onClick={handleCopyReport} 
              className="btn btn-secondary" 
              style={{ padding: '12px 24px', fontSize: '0.9rem', fontWeight: 600 }}
            >
              {copied ? <Check size={16} color="#087455" /> : <Copy size={16} />}
              {copied ? 'Đã sao chép kết quả!' : 'Sao chép toàn bộ báo cáo'}
            </button>
          </div>

        </div>
      )}

    </div>
  );
}

