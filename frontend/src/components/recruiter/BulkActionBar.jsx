/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useState } from 'react';
import { CheckCircle2, LoaderCircle, Tags, Users, X } from 'lucide-react';
import { executeBulkAction } from '../../services/recruiterApi';

export default function BulkActionBar({ jobId, selected, versions, onClear, onCompleted, onCompare }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  if (!selected.length) return null;

  const execute = async (action, value) => {
    if (!window.confirm(`Áp dụng hành động cho ${selected.length} hồ sơ đã chọn?`)) return;
    setBusy(true); setMessage('');
    try {
      const result = await executeBulkAction(jobId, { action, value, application_ids: selected, expected_versions: versions });
      setMessage(`${result.success_count} thành công${result.failure_count ? ` · ${result.failure_count} cần kiểm tra` : ''}`);
      onCompleted(result);
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };

  return <div className="bulk-action-bar">
    <strong><Users size={16} /> {selected.length} hồ sơ đã chọn</strong>
    <div>
      <button disabled={busy} onClick={() => execute('MOVE_STAGE', 'RECRUITER_REVIEW')}>Chuyển sang đang xem</button>
      <button disabled={busy} onClick={() => execute('MOVE_STAGE', 'SHORTLISTED')}><CheckCircle2 size={14} /> Shortlist</button>
      <button disabled={busy} onClick={() => { const tag = window.prompt('Tên nhãn muốn gắn:'); if (tag?.trim()) execute('ADD_TAG', tag.trim()); }}><Tags size={14} /> Gắn nhãn</button>
      <button disabled={busy || selected.length < 2 || selected.length > 5} onClick={onCompare}>So sánh 2–5 hồ sơ</button>
      {busy && <LoaderCircle className="workspace-state__spin" size={16} />}
      {message && <span>{message}</span>}
      <button aria-label="Bỏ chọn tất cả" onClick={onClear}><X size={15} /></button>
    </div>
  </div>;
}
