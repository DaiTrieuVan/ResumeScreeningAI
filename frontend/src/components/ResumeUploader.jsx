import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, XCircle } from 'lucide-react';
import { uploadSingleResume } from '../services/api';

export default function ResumeUploader({ jobId, onResumesUploaded }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]); // array of File objects
  const [fileProgressMap, setFileProgressMap] = useState({}); // { [fileName]: { status: 'pending'|'uploading'|'success'|'error', errorMsg?: string } }
  const [uploading, setUploading] = useState(false);
  const [completedCount, setCompletedCount] = useState(0);
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
      addFiles(validPdfs);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const validPdfs = Array.from(e.target.files).filter(
        (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf')
      );
      addFiles(validPdfs);
    }
  };

  const addFiles = (newFiles) => {
    setSelectedFiles((prev) => {
      const existingNames = new Set(prev.map(f => f.name));
      const filtered = newFiles.filter(f => !existingNames.has(f.name));
      return [...prev, ...filtered];
    });
  };

  const clearFiles = () => {
    if (uploading) return;
    setSelectedFiles([]);
    setFileProgressMap({});
    setCompletedCount(0);
    setStatusMsg(null);
  };

  const handleUploadSubmit = async () => {
    if (!selectedFiles.length || uploading) return;

    setUploading(true);
    setStatusMsg(null);
    setCompletedCount(0);

    const initialMap = {};
    selectedFiles.forEach(f => {
      initialMap[f.name] = { status: 'pending' };
    });
    setFileProgressMap(initialMap);

    const uploadedResults = [];
    let successCount = 0;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];

      // Mark current file uploading
      setFileProgressMap(prev => ({
        ...prev,
        [file.name]: { status: 'uploading' }
      }));

      try {
        const result = await uploadSingleResume(file, jobId);
        uploadedResults.push(result);
        successCount++;

        setFileProgressMap(prev => ({
          ...prev,
          [file.name]: { status: 'success' }
        }));
      } catch (err) {
        setFileProgressMap(prev => ({
          ...prev,
          [file.name]: { status: 'error', errorMsg: err.message }
        }));
      }

      setCompletedCount(i + 1);
    }

    setUploading(false);

    if (successCount > 0) {
      setStatusMsg({
        type: 'success',
        text: `Đã tải lên và trích xuất thành công ${successCount}/${selectedFiles.length} file CV PDF.`
      });
      if (onResumesUploaded) onResumesUploaded(uploadedResults);
    } else {
      setStatusMsg({
        type: 'error',
        text: 'Tất cả các file CV PDF đều gặp lỗi trong quá trình tải lên hoặc trích xuất.'
      });
    }
  };

  const uploadPercent = selectedFiles.length > 0 ? Math.round((completedCount / selectedFiles.length) * 100) : 0;

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
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'var(--border-color)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '28px 16px',
          textAlign: 'center',
          background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'rgba(0, 0, 0, 0.2)',
          cursor: uploading ? 'not-allowed' : 'pointer',
          transition: 'var(--transition)',
          opacity: uploading ? 0.7 : 1
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf"
          disabled={uploading}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        <UploadCloud size={36} color="var(--accent-cyan)" style={{ marginBottom: '8px' }} />
        <p style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '4px' }}>
          Kéo & thả file CV PDF vào đây, hoặc <span style={{ color: 'var(--accent-primary)' }}>bấm để chọn file</span>
        </p>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Hỗ trợ tải lên nhiều file PDF cùng lúc. Trích xuất thông tin tự động theo thời gian thực.
        </p>
      </div>

      {/* Upload Progress Bar when uploading or completed */}
      {uploading && (
        <div style={{ marginTop: '16px', background: 'rgba(0, 0, 0, 0.3)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, marginBottom: '6px' }}>
            <span style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Loader2 size={14} className="spin" /> Đang trích xuất: {completedCount} / {selectedFiles.length} CVs
            </span>
            <span style={{ color: '#fff' }}>{uploadPercent}%</span>
          </div>
          <div style={{ height: '8px', width: '100%', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '6px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${uploadPercent}%`,
              background: 'linear-gradient(90deg, #6366f1, #38bdf8)',
              borderRadius: '6px',
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>
      )}

      {/* Selected File Chips with Status Indicators */}
      {selectedFiles.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>File CV đã chọn ({selectedFiles.length}):</span>
            {!uploading && (
              <button onClick={clearFiles} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: '0.75rem' }}>
                Xóa tất cả
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '140px', overflowY: 'auto', marginBottom: '14px' }}>
            {selectedFiles.map((f, idx) => {
              const statusInfo = fileProgressMap[f.name] || { status: 'pending' };
              let badgeBg = 'rgba(255,255,255,0.06)';
              let badgeBorder = 'var(--border-color)';
              let icon = <FileText size={12} color="var(--accent-cyan)" />;

              if (statusInfo.status === 'uploading') {
                badgeBg = 'rgba(99, 102, 241, 0.2)';
                badgeBorder = 'rgba(99, 102, 241, 0.4)';
                icon = <Loader2 size={12} className="spin" color="var(--accent-cyan)" />;
              } else if (statusInfo.status === 'success') {
                badgeBg = 'rgba(16, 185, 129, 0.15)';
                badgeBorder = 'rgba(16, 185, 129, 0.4)';
                icon = <CheckCircle2 size={12} color="#34d399" />;
              } else if (statusInfo.status === 'error') {
                badgeBg = 'rgba(244, 63, 94, 0.15)';
                badgeBorder = 'rgba(244, 63, 94, 0.4)';
                icon = <XCircle size={12} color="#f87171" />;
              }

              return (
                <span key={idx} style={{
                  fontSize: '0.75rem', background: badgeBg, padding: '5px 10px', borderRadius: '6px',
                  display: 'inline-flex', alignItems: 'center', gap: '6px', border: `1px solid ${badgeBorder}`,
                  transition: 'all 0.2s ease'
                }}>
                  {icon}
                  {f.name}
                  {statusInfo.status === 'uploading' && <span style={{ fontSize: '0.68rem', color: 'var(--accent-cyan)' }}>[Đang xử lý...]</span>}
                  {statusInfo.status === 'success' && <span style={{ fontSize: '0.68rem', color: '#34d399' }}>[Thành công]</span>}
                  {statusInfo.status === 'error' && <span style={{ fontSize: '0.68rem', color: '#f87171' }}>[Lỗi]</span>}
                </span>
              );
            })}
          </div>

          <button
            onClick={handleUploadSubmit}
            className="btn btn-primary"
            disabled={uploading}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="spin" /> Đang trích xuất PDF ({completedCount}/{selectedFiles.length})...
              </>
            ) : (
              `Tải lên & Trích xuất ${selectedFiles.length} CV`
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
