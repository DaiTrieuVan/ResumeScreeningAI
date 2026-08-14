import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadResumes } from '../services/api';

export default function ResumeUploader({ onResumesUploaded }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const validPdfs = Array.from(e.dataTransfer.files).filter(
        (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf')
      );
      setSelectedFiles((prev) => [...prev, ...validPdfs]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const validPdfs = Array.from(e.target.files).filter(
        (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf')
      );
      setSelectedFiles((prev) => [...prev, ...validPdfs]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFiles.length) return;
    setUploading(true);
    setStatusMsg(null);

    try {
      const uploaded = await uploadResumes(selectedFiles);
      setStatusMsg({ type: 'success', text: `Tải lên và trích xuất thành công ${uploaded.length} hồ sơ CV.` });
      setSelectedFiles([]);
      if (onResumesUploaded) onResumesUploaded(uploaded);
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Tải lên thất bại: ' + err.message });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <UploadCloud color="var(--accent-primary)" size={18} />
        Tải lên CV Ứng viên hàng loạt (Định dạng PDF)
      </h3>

      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'var(--border-color)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '32px 16px',
          textAlign: 'center',
          background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'rgba(0, 0, 0, 0.2)',
          cursor: 'pointer',
          transition: 'var(--transition)'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        <UploadCloud size={40} color="var(--accent-cyan)" style={{ marginBottom: '10px' }} />
        <p style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '4px' }}>
          Kéo & thả file CV PDF vào đây, hoặc <span style={{ color: 'var(--accent-primary)' }}>bấm để chọn file</span>
        </p>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Hỗ trợ tải lên nhiều file PDF cùng lúc, tối đa 10MB mỗi file
        </p>
      </div>

      {/* File List */}
      {selectedFiles.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>File CV đã chọn ({selectedFiles.length}):</span>
            <button onClick={() => setSelectedFiles([])} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: '0.75rem' }}>
              Xóa tất cả
            </button>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '120px', overflowY: 'auto', marginBottom: '14px' }}>
            {selectedFiles.map((f, idx) => (
              <span key={idx} style={{
                fontSize: '0.75rem', background: 'rgba(255,255,255,0.06)', padding: '4px 10px', borderRadius: '6px',
                display: 'inline-flex', alignItems: 'center', gap: '6px', border: '1px solid var(--border-color)'
              }}>
                <FileText size={12} color="var(--accent-cyan)" />
                {f.name}
              </span>
            ))}
          </div>

          <button
            onClick={handleUploadSubmit}
            className="btn btn-primary"
            disabled={uploading}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="spin" /> Đang xử lý & trích xuất văn bản PDF...
              </>
            ) : (
              `Tải lên & Phân tích ${selectedFiles.length} CV`
            )}
          </button>
        </div>
      )}

      {/* Status Messages */}
      {statusMsg && (
        <div style={{
          marginTop: '14px', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem',
          display: 'flex', alignItems: 'center', gap: '8px',
          background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
          color: statusMsg.type === 'success' ? '#34d399' : '#f87171',
          border: `1px solid ${statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`
        }}>
          {statusMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          {statusMsg.text}
        </div>
      )}
    </div>
  );
}
