/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useEffect, useState } from 'react';
import { Check, Clock3, MessageSquarePlus, Send, XCircle } from 'lucide-react';

import { appendCandidateDecision, fetchDecisionTimeline } from '../../services/recruiterApi';

const STAGES = [
  ['AI_ANALYZED', 'AI đã phân tích'], ['RECRUITER_REVIEW', 'Recruiter đang xem'],
  ['SHORTLISTED', 'Shortlist'], ['HR_INTERVIEW', 'Phỏng vấn HR'],
  ['TECH_INTERVIEW', 'Phỏng vấn chuyên môn'], ['OFFER', 'Đề nghị tuyển dụng'],
  ['HIRED', 'Đã tuyển'], ['REJECTED', 'Từ chối'],
];
const REASONS = [['SKILL_GAP', 'Thiếu kỹ năng bắt buộc'], ['EXPERIENCE_GAP', 'Kinh nghiệm chưa phù hợp'], ['SALARY_MISMATCH', 'Không phù hợp ngân sách'], ['OTHER', 'Lý do khác']];

export default function DecisionPanel({ applicationId, version, currentStage, onUpdated }) {
  const [events, setEvents] = useState([]);
  const [stage, setStage] = useState(currentStage);
  const [note, setNote] = useState('');
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const loadTimeline = () => fetchDecisionTimeline(applicationId).then(setEvents).catch((err) => setError(err.message));
  useEffect(() => { loadTimeline(); }, [applicationId]);
  useEffect(() => setStage(currentStage), [currentStage]);

  const submit = async (payload) => {
    setBusy(true); setError('');
    try {
      const event = await appendCandidateDecision(applicationId, version, payload);
      setEvents((current) => [event, ...current]);
      setNote(''); setReason('');
      onUpdated?.(event);
    } catch (err) {
      setError(err.status === 409 ? 'Hồ sơ vừa được người khác cập nhật. Đang tải lại phiên bản mới…' : err.message);
      if (err.status === 409) onUpdated?.();
    } finally { setBusy(false); }
  };

  const changeStage = () => {
    if (stage === 'REJECTED' && !reason) { setError('Vui lòng chọn lý do trước khi từ chối ứng viên.'); return; }
    submit({ event_type: stage === 'REJECTED' ? 'HUMAN_DECISION' : 'STAGE_CHANGED', to_stage: stage, decision: stage === 'REJECTED' ? 'REJECT' : undefined, reason_code: reason || undefined, note: note || undefined });
  };

  return <section className="decision-panel">
    <div className="candidate-review__section-heading"><div><Clock3 size={17} /><strong>Quyết định tuyển dụng</strong></div><span>Phiên bản {version}</span></div>
    <div className="decision-panel__controls">
      <label>Giai đoạn<select value={stage} onChange={(e) => setStage(e.target.value)}>{STAGES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      {stage === 'REJECTED' && <label>Lý do từ chối *<select aria-label="Lý do từ chối" value={reason} onChange={(e) => setReason(e.target.value)}><option value="">Chọn lý do</option>{REASONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>}
      <label>Ghi chú nội bộ<textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Thêm bối cảnh cho đồng đội…" /></label>
      <div className="decision-panel__actions"><button disabled={busy || !note.trim()} onClick={() => submit({ event_type: 'NOTE_ADDED', note })}><MessageSquarePlus size={14} /> Lưu ghi chú</button><button className="is-primary" disabled={busy || stage === currentStage} onClick={changeStage}>{stage === 'REJECTED' ? <XCircle size={14} /> : <Check size={14} />} Cập nhật giai đoạn</button></div>
      {error && <p className="decision-panel__error">{error}</p>}
    </div>
    <div className="decision-timeline">
      {events.length === 0 ? <p>Chưa có hoạt động của recruiter.</p> : events.map((event) => <article key={event.id}><span className="decision-timeline__dot" /><div><strong>{event.event_type === 'NOTE_ADDED' ? 'Đã thêm ghi chú' : event.decision === 'REJECT' ? 'Đã từ chối ứng viên' : `Chuyển sang ${STAGES.find(([value]) => value === event.to_stage)?.[1] || event.to_stage}`}</strong>{event.note && <p>{event.note}</p>}<small>{event.actor_id} · {new Date(event.created_at).toLocaleString('vi-VN')}</small></div></article>)}
    </div>
  </section>;
}
