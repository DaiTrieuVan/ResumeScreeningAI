/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useEffect, useMemo, useState } from 'react';
import { Activity, AlertTriangle, CheckCircle2, Clock3, Copy, RefreshCw } from 'lucide-react';
import { fetchRecruiterAnalytics } from '../../services/recruiterApi';

const LABELS = { RECEIVED: 'Mới nhận', AI_ANALYZED: 'AI phân tích', RECRUITER_REVIEW: 'Đang xem', SHORTLISTED: 'Shortlist', HR_INTERVIEW: 'PV HR', TECH_INTERVIEW: 'PV chuyên môn', OFFER: 'Đề nghị', HIRED: 'Đã tuyển', REJECTED: 'Từ chối' };

export default function RecruiterAnalytics({ jobId, refreshToken }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { let active = true; setError(''); fetchRecruiterAnalytics(jobId).then((value) => active && setData(value)).catch((reason) => active && setError(reason.message)); return () => { active = false; }; }, [jobId, refreshToken]);
  const total = useMemo(() => data ? Object.values(data.funnel).reduce((sum, count) => sum + count, 0) : 0, [data]);
  if (error) return <div className="workspace-state workspace-state--error">{error}</div>;
  if (!data) return <div className="workspace-state"><RefreshCw className="workspace-state__spin" size={17} /> Đang tổng hợp vận hành…</div>;
  const upload = data.upload_counts;
  return <section className="recruiter-analytics glass-panel">
    <div className="panel-heading"><div><span className="section-eyebrow"><Activity size={15} /> Sức khỏe quy trình</span><h3>Funnel và chất lượng xử lý</h3></div><small>Cập nhật theo vị trí đang chọn</small></div>
    <div className="analytics-layout">
      <div className="funnel-chart" aria-label="Funnel tuyển dụng">{Object.entries(data.funnel).map(([stage, count]) => <div key={stage}><span><b>{LABELS[stage] || stage}</b><em>{count}</em></span><div><i style={{ width: `${Math.max(4, total ? count / total * 100 : 0)}%` }} /></div></div>)}</div>
      <div className="analytics-stats">
        <article><CheckCircle2 /><div><span>CV xử lý thành công</span><strong>{upload.success}/{upload.total}</strong></div></article>
        <article><AlertTriangle /><div><span>CV lỗi</span><strong>{upload.failed}</strong></div></article>
        <article><Copy /><div><span>Nghi trùng lặp</span><strong>{upload.duplicate}</strong></div></article>
        <article><Clock3 /><div><span>Thời gian lô trung vị</span><strong>{data.median_processing_seconds}s</strong></div></article>
        <article><RefreshCw /><div><span>Recruiter override AI</span><strong>{Math.round(data.ai_override_rate * 100)}%</strong></div></article>
      </div>
    </div>
  </section>;
}
