/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { AlertCircle, Inbox, LoaderCircle, RefreshCw } from 'lucide-react';

export function WorkspaceLoading({ label = 'Đang tải dữ liệu tuyển dụng…' }) {
  return (
    <div className="workspace-state" role="status" aria-live="polite">
      <LoaderCircle className="workspace-state__spin" size={22} />
      <span>{label}</span>
    </div>
  );
}

export function WorkspaceEmpty({ title = 'Chưa có dữ liệu', description, action }) {
  return (
    <div className="workspace-state workspace-state--stacked">
      <Inbox size={28} aria-hidden="true" />
      <strong>{title}</strong>
      {description && <p>{description}</p>}
      {action}
    </div>
  );
}

export function WorkspaceError({ message, onRetry }) {
  return (
    <div className="workspace-state workspace-state--error" role="alert">
      <AlertCircle size={22} aria-hidden="true" />
      <span>{message || 'Đã có lỗi xảy ra.'}</span>
      {onRetry && (
        <button type="button" className="btn btn-secondary" onClick={onRetry}>
          <RefreshCw size={15} /> Thử lại
        </button>
      )}
    </div>
  );
}

export function StaleResultNotice({ onReevaluate }) {
  return (
    <div className="workspace-stale" role="status">
      <div>
        <strong>Kết quả đang dùng bộ tiêu chí cũ</strong>
        <p>Điểm chính thức không đổi cho đến khi bạn chủ động chạy đánh giá lại.</p>
      </div>
      {onReevaluate && (
        <button type="button" className="btn btn-secondary" onClick={onReevaluate}>
          Chạy lại đánh giá
        </button>
      )}
    </div>
  );
}
