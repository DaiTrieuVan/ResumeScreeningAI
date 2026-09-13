/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useEffect, useRef, useState } from 'react';
import { FilePlus2, UploadCloud, X } from 'lucide-react';

import { createUploadBatch, fetchUploadBatch } from '../../services/recruiterApi';
import BatchReviewPanel from './BatchReviewPanel';
import { WorkspaceError } from './WorkspaceStates';


const terminalStatuses = new Set(['COMPLETED', 'COMPLETED_WITH_ERRORS', 'CANCELLED']);

export default function BatchUploader({ jobId, criteriaSetId, onBatchCompleted }) {
  const [files, setFiles] = useState([]);
  const [batch, setBatch] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);
  const storageKey = jobId ? `recruiter:last-batch:${jobId}` : null;

  const acceptFiles = (incoming) => {
    const pdfs = Array.from(incoming).filter((file) => file.name.toLowerCase().endsWith('.pdf'));
    setFiles((current) => {
      const keys = new Set(current.map((file) => `${file.name}:${file.size}:${file.lastModified}`));
      return [...current, ...pdfs.filter((file) => !keys.has(`${file.name}:${file.size}:${file.lastModified}`))].slice(0, 200);
    });
  };

  useEffect(() => {
    setFiles([]);
    setBatch(null);
    setError('');
    if (!storageKey) return;
    const batchId = localStorage.getItem(storageKey);
    if (batchId) fetchUploadBatch(batchId).then(setBatch).catch(() => localStorage.removeItem(storageKey));
  }, [storageKey]);

  useEffect(() => {
    if (!batch || terminalStatuses.has(batch.status)) {
      if (batch && terminalStatuses.has(batch.status)) onBatchCompleted?.(batch);
      return undefined;
    }
    const timer = window.setInterval(async () => {
      try { setBatch(await fetchUploadBatch(batch.id)); } catch (requestError) { setError(requestError.message); }
    }, 1200);
    return () => window.clearInterval(timer);
  }, [batch?.id, batch?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const startUpload = async () => {
    if (!jobId || !files.length) return;
    setUploading(true);
    setError('');
    try {
      const created = await createUploadBatch(jobId, files, criteriaSetId);
      setBatch(created);
      localStorage.setItem(storageKey, created.id);
      setFiles([]);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="batch-uploader">
      <div className="batch-uploader__heading">
        <div>
          <span className="section-eyebrow"><UploadCloud size={15} /> Tiếp nhận CV hàng loạt</span>
          <h3>Tải tối đa 200 CV trong một lô</h3>
        </div>
        {batch && terminalStatuses.has(batch.status) && (
          <button type="button" className="btn btn-secondary" onClick={() => { setBatch(null); localStorage.removeItem(storageKey); }}>
            <FilePlus2 size={15} /> Lô mới
          </button>
        )}
      </div>

      {!batch && (
        <>
          <div
            className={`batch-dropzone ${dragging ? 'is-dragging' : ''}`}
            onDragEnter={(event) => { event.preventDefault(); setDragging(true); }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => { event.preventDefault(); setDragging(false); acceptFiles(event.dataTransfer.files); }}
            onClick={() => inputRef.current?.click()}
            role="button" tabIndex={0}
            onKeyDown={(event) => event.key === 'Enter' && inputRef.current?.click()}
          >
            <input ref={inputRef} type="file" accept=".pdf,application/pdf" multiple hidden onChange={(event) => acceptFiles(event.target.files)} />
            <UploadCloud size={30} />
            <strong>Kéo thả CV PDF hoặc bấm để chọn</strong>
            <span>Mỗi CV tối đa 15 MB · Lỗi một tệp không làm dừng cả lô</span>
          </div>

          {files.length > 0 && (
            <div className="batch-selection">
              <div><strong>{files.length} CV đã sẵn sàng</strong><span>{Math.max(0, 200 - files.length)} vị trí còn lại trong lô</span></div>
              <button type="button" className="btn btn-primary" onClick={startUpload} disabled={uploading}>{uploading ? 'Đang tạo lô…' : `Tải lên ${files.length} CV`}</button>
              <button type="button" className="batch-selection__clear" onClick={() => setFiles([])} aria-label="Xóa danh sách"><X size={16} /></button>
            </div>
          )}
        </>
      )}

      {error && <WorkspaceError message={error} />}
      {batch && <BatchReviewPanel batch={batch} onUpdated={setBatch} />}
    </section>
  );
}
