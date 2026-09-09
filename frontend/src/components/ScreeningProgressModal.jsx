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
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '560px',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 30px rgba(99, 102, 241, 0.2)',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        animation: 'fadeIn 0.2s ease-out'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--accent-primary, #6366f1), var(--accent-cyan, #06b6d4))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Sparkles size={20} color="#fff" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: '#fff' }}>
                Động cơ Sàng lọc AI
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted, #94a3b8)', margin: 0 }}>
                {isCompleted ? 'Hoàn tất phân tích dữ liệu' : 'Đang xử lý & trích xuất AI hai giai đoạn'}
              </p>
            </div>
          </div>

          {isCompleted && (
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: 'none',
                color: '#fff',
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
            <span style={{ fontWeight: 700, color: '#fff' }}>{percent}%</span>
          </div>

          {/* Bar track */}
          <div style={{
            height: '10px',
            width: '100%',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '10px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              height: '100%',
              width: `${percent}%`,
              background: error
                ? 'linear-gradient(90deg, #ef4444, #f87171)'
                : 'linear-gradient(90deg, #6366f1, #38bdf8, #34d399)',
              borderRadius: '10px',
              transition: 'width 0.4s ease-out'
            }} />
          </div>

          {/* Counts */}
          {total > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted, #94a3b8)', marginTop: '6px' }}>
              <span>Đã hoàn thành: <b>{current} / {total}</b> CVs</span>
              <span>{total - current} CV đang chờ</span>
            </div>
          )}
        </div>

        {/* Current status message banner */}
        <div style={{
          padding: '12px 14px',
          borderRadius: '10px',
          backgroundColor: error ? 'rgba(239, 68, 68, 0.12)' : isCompleted ? 'rgba(16, 185, 129, 0.12)' : 'rgba(99, 102, 241, 0.12)',
          border: `1px solid ${error ? 'rgba(239, 68, 68, 0.3)' : isCompleted ? 'rgba(16, 185, 129, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`,
          marginBottom: '16px',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: error ? '#fca5a5' : isCompleted ? '#6ee7b7' : '#a5b4fc'
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
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '12px',
            maxHeight: '130px',
            overflowY: 'auto',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            marginBottom: '16px'
          }}
        >
          <div style={{ color: 'var(--text-muted, #64748b)', marginBottom: '6px', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Nhật ký thực thi (Live Console Log):
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
          {isCompleted ? 'Xem Kết quả Sàng lọc Hoàn tất' : 'Đóng / Chạy ngầm phía dưới'}
        </button>
      </div>
    </div>
  );
}
