import React, { useEffect, useRef } from 'react';
import { Cpu, CheckCircle2, AlertCircle, Loader2, Sparkles, X } from 'lucide-react';

export default function ScreeningProgressModal({ isOpen, progressData, logs, isCompleted, error, onClose }) {
  const consoleBoxRef = useRef(null);

  useEffect(() => {
    if (consoleBoxRef.current) {
      consoleBoxRef.current.scrollTop = consoleBoxRef.current.scrollHeight;
    }
  }, [logs]);

  if (!isOpen) return null;

  const percent = progressData?.progress_percent || 0;
  const current = progressData?.current || 0;
  const total = progressData?.total || 0;
  const message = progressData?.message || 'Đang chuẩn bị dữ liệu phân tích...';
  const candidateName = progressData?.current_candidate;

  return (
    <div className="modal-overlay" role="presentation">
      <div className="glass-panel modal-card" role="dialog" aria-modal="true" aria-label="Tiến độ sàng lọc AI" style={{
        width: '100%',
        maxWidth: '560px',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 24px 64px rgba(13, 38, 29, 0.18)',
        border: '1px solid var(--border-glow)',
        animation: 'fadeIn 0.2s ease-out'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'var(--accent-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={20} color="#fff" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                Tiến độ sàng lọc AI
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted, #94a3b8)', margin: 0 }}>
                {isCompleted ? 'Đã hoàn tất phân tích hồ sơ' : 'Bạn có thể theo dõi tiến độ theo thời gian thực'}
              </p>
            </div>
          </div>

          {isCompleted && (
            <button
              onClick={onClose}
              style={{
                background: '#f3f6f5',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                borderRadius: '8px',
                width: '32px',
                height: '32px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Progress Bar Container */}
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', fontSize: '0.85rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--accent-cyan, #38bdf8)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              {!isCompleted && !error && <Loader2 size={14} className="spin" />}
              {isCompleted ? 'Đã hoàn thành' : error ? 'Xảy ra lỗi' : candidateName ? `Đang xử lý: ${candidateName}` : 'Đang thực hiện'}
            </span>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{percent}%</span>
          </div>

          {/* Bar track */}
          <div style={{
            height: '10px',
            width: '100%',
            backgroundColor: '#dfe9e5',
            borderRadius: '10px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              height: '100%',
              width: `${percent}%`,
              background: error
                ? 'linear-gradient(90deg, #ef4444, #f87171)'
                : 'var(--accent-gradient)',
              borderRadius: '10px',
              transition: 'width 0.4s ease-out'
            }} />
          </div>

          {/* Counts */}
          {total > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)', marginTop: '6px' }}>
              <span>Đã hoàn thành: <b>{current} / {total}</b> CV</span>
              <span>Còn {total - current} CV</span>
            </div>
          )}
        </div>

        {/* Current status message banner */}
        <div style={{
          padding: '12px 14px',
          borderRadius: '10px',
          backgroundColor: error ? '#fff0f1' : isCompleted ? '#e5f6ef' : '#eef7f4',
          border: `1px solid ${error ? '#f0c7cb' : isCompleted ? '#bde7d8' : '#cce5dc'}`,
          marginBottom: '16px',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: error ? '#b84250' : isCompleted ? '#087455' : '#276f59'
        }}>
          {error ? (
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
          ) : isCompleted ? (
            <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
          ) : (
            <Cpu size={18} style={{ flexShrink: 0 }} className="spin" />
          )}
          <span style={{ fontWeight: 500 }}>{error || message}</span>
        </div>

        {/* Live Event Console Log */}
        <div 
          ref={consoleBoxRef}
          style={{
            backgroundColor: '#17231f',
            borderRadius: '10px',
            border: '1px solid #263b34',
            padding: '12px',
            maxHeight: '130px',
            overflowY: 'auto',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            marginBottom: '16px'
          }}
        >
          <div style={{ color: 'var(--text-muted, #64748b)', marginBottom: '6px', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Nhật ký xử lý trực tiếp
          </div>
          {(logs || []).map((log, idx) => (
            <div key={idx} style={{ color: '#cbd5e1', marginBottom: '4px', display: 'flex', gap: '8px' }}>
              <span style={{ color: 'var(--text-muted, #64748b)', flexShrink: 0 }}>[{log.time}]</span>
              <span>{log.text}</span>
            </div>
          ))}
        </div>

        {/* Action button when complete */}
        <button
          onClick={onClose}
          className={`btn ${isCompleted ? 'btn-primary' : 'btn-secondary'}`}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {isCompleted ? <CheckCircle2 size={16} /> : <X size={16} />}
          {isCompleted ? 'Xem kết quả sàng lọc' : 'Đóng và tiếp tục chạy nền'}
        </button>
      </div>
    </div>
  );
}
