/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useState } from 'react';
import {
  AlertTriangle, CheckCircle2, FileText, Link2, LoaderCircle, RefreshCw, RotateCcw, SkipForward, Users,
} from 'lucide-react';

import { recoverUploadBatch, resolveUploadDuplicate, retryUploadBatch, submitManualRecovery } from '../../services/recruiterApi';


const statusLabels = {
  QUEUED: 'Đang chờ', VALIDATING: 'Đang kiểm tra', PARSING: 'Đang đọc CV',
  NEEDS_OCR: 'Cần OCR', DEDUPE_REVIEW: 'Có thể trùng', READY: 'Sẵn sàng',
  EVALUATING: 'Đang đánh giá', COMPLETED: 'Hoàn tất', FAILED: 'Lỗi', CANCELLED: 'Đã bỏ qua',
};

export default function BatchReviewPanel({ batch, onUpdated }) {
  const [busyItem, setBusyItem] = useState(null);
  const [retrying, setRetrying] = useState(false);
  const [recovering, setRecovering] = useState(false);
  const [manualValues, setManualValues] = useState({});
  if (!batch) return null;

  const completed = batch.success_count + batch.failed_count + batch.duplicate_count + batch.cancelled_count;
  const percent = batch.total_count ? Math.round((completed / batch.total_count) * 100) : 0;
  const failedItems = batch.items.filter((item) => ['FAILED', 'NEEDS_OCR'].includes(item.status));

  const retryFailed = async () => {
    setRetrying(true);
    try { onUpdated?.(await retryUploadBatch(batch.id)); } finally { setRetrying(false); }
  };

  const resolve = async (itemId, resolution) => {
    setBusyItem(itemId);
    try { onUpdated?.(await resolveUploadDuplicate(itemId, resolution)); } finally { setBusyItem(null); }
  };

  const recoverInterrupted = async () => {
    setRecovering(true);
    try { onUpdated?.(await recoverUploadBatch(batch.id)); } finally { setRecovering(false); }
  };

  const recoverManual = async (itemId) => {
    const current = manualValues[itemId] || {};
    setBusyItem(itemId);
    try {
      onUpdated?.(await submitManualRecovery(itemId, current.text || '', current.reason || 'Đã đối chiếu bản scan'));
    } finally { setBusyItem(null); }
  };

  return (
    <div className="batch-review" aria-live="polite">
      <div className="batch-review__summary">
        <div>
          <span className="section-eyebrow"><Users size={14} /> Tiến độ lô CV</span>
          <strong>{completed}/{batch.total_count} hồ sơ đã xử lý</strong>
        </div>
        <span className="batch-review__percent">{percent}%</span>
      </div>
      <div className="batch-progress" aria-label={`Tiến độ ${percent}%`}>
        <span style={{ width: `${percent}%` }} />
      </div>
      <div className="batch-review__counts">
        <span className="is-success"><CheckCircle2 size={13} /> {batch.success_count} thành công</span>
        <span className="is-warning"><AlertTriangle size={13} /> {batch.duplicate_count} trùng</span>
        <span className="is-error"><AlertTriangle size={13} /> {batch.failed_count} cần xử lý</span>
      </div>

      <div className="batch-items">
        {batch.items.map((item) => (
          <article key={item.id} className={`batch-item batch-item--${item.status.toLowerCase()}`}>
            <FileText size={17} aria-hidden="true" />
            <div className="batch-item__body">
              <strong title={item.original_file_name}>{item.original_file_name}</strong>
              <span>{item.user_message || statusLabels[item.status] || item.status}</span>
            </div>
            {['QUEUED', 'VALIDATING', 'PARSING', 'EVALUATING'].includes(item.status) && <LoaderCircle className="workspace-state__spin" size={16} />}
            {item.status === 'COMPLETED' && <CheckCircle2 className="is-success" size={17} />}
            {item.status === 'DEDUPE_REVIEW' && (
              <div className="batch-item__actions">
                <button type="button" onClick={() => resolve(item.id, 'LINK_EXISTING')} disabled={busyItem === item.id}><Link2 size={13} /> Dùng hồ sơ cũ</button>
                <button type="button" onClick={() => resolve(item.id, 'KEEP_BOTH')} disabled={busyItem === item.id}>Giữ cả hai</button>
                <button type="button" onClick={() => resolve(item.id, 'SKIP')} disabled={busyItem === item.id}><SkipForward size={13} /> Bỏ qua</button>
              </div>
            )}
            {item.status === 'NEEDS_OCR' && (
              <details className="batch-item__manual">
                <summary>Nhập nội dung đã xác minh</summary>
                <label>Văn bản từ CV
                  <textarea aria-label={`Văn bản xác minh cho ${item.original_file_name}`} minLength={20} value={manualValues[item.id]?.text || ''} onChange={(event) => setManualValues((values) => ({ ...values, [item.id]: { ...values[item.id], text: event.target.value } }))} />
                </label>
                <label>Lý do
                  <input aria-label={`Lý do xác minh cho ${item.original_file_name}`} value={manualValues[item.id]?.reason || ''} onChange={(event) => setManualValues((values) => ({ ...values, [item.id]: { ...values[item.id], reason: event.target.value } }))} placeholder="Đã đối chiếu bản scan" />
                </label>
                <button type="button" disabled={(manualValues[item.id]?.text || '').length < 20 || busyItem === item.id} onClick={() => recoverManual(item.id)}>Xác nhận và xử lý lại</button>
              </details>
            )}
            {item.error_code === 'RETRY_LIMIT_REACHED' && <span className="batch-item__limit">Đã dừng tự động — cần thay tệp hoặc xác minh thủ công.</span>}
          </article>
        ))}
      </div>

      {failedItems.length > 0 && (
        <button type="button" className="btn btn-secondary batch-review__retry" onClick={retryFailed} disabled={retrying}>
          <RefreshCw size={15} className={retrying ? 'spin' : ''} /> Thử lại {failedItems.length} mục lỗi
        </button>
      )}
      {batch.status === 'PROCESSING' && (
        <button type="button" className="btn btn-secondary batch-review__retry" onClick={recoverInterrupted} disabled={recovering}>
          <RotateCcw size={15} className={recovering ? 'spin' : ''} /> Phục hồi tiến trình gián đoạn
        </button>
      )}
    </div>
  );
}
