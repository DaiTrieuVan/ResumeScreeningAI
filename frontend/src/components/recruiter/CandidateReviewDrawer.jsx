/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React, { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  AlertCircle, CheckCircle2, ExternalLink, FilePenLine, FileText, HelpCircle,
  LoaderCircle, LocateFixed, ShieldCheck, X, XCircle,
} from 'lucide-react';

import { correctCandidateData, fetchCandidateDetail, getOriginalResumeUrl } from '../../services/recruiterApi';
import DecisionPanel from './DecisionPanel';

const RESULT_META = {
  MET: { label: 'Đạt', icon: CheckCircle2, className: 'is-met' },
  PARTIAL: { label: 'Đạt một phần', icon: AlertCircle, className: 'is-partial' },
  NOT_MET: { label: 'Chưa đạt', icon: XCircle, className: 'is-not-met' },
  UNKNOWN: { label: 'Chưa đủ dữ liệu', icon: HelpCircle, className: 'is-unknown' },
  NOT_APPLICABLE: { label: 'Không áp dụng', icon: AlertCircle, className: 'is-na' },
  'N/A': { label: 'Không áp dụng', icon: AlertCircle, className: 'is-na' },
};

function ResultBadge({ result }) {
  const meta = RESULT_META[result] || RESULT_META.UNKNOWN;
  const Icon = meta.icon;
  return <span className={`evidence-result ${meta.className}`}><Icon size={14} />{meta.label}</span>;
}

const CORRECTION_FIELDS = [
  ['extracted_skills', 'Kỹ năng', true],
  ['work_history', 'Kinh nghiệm', true],
  ['education', 'Học vấn', true],
  ['parsed_name', 'Họ tên', false],
  ['parsed_email', 'Email', false],
  ['parsed_phone', 'Số điện thoại', false],
];

function CorrectionPanel({ detail, onCorrected }) {
  const [field, setField] = useState('extracted_skills');
  const [value, setValue] = useState(JSON.stringify(detail.extracted_skills || [], null, 2));
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const changeField = (nextField) => {
    setField(nextField);
    const [, , listField] = CORRECTION_FIELDS.find(([key]) => key === nextField);
    const current = detail[nextField] ?? (listField ? [] : '');
    setValue(listField ? JSON.stringify(current, null, 2) : String(current));
  };

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    const [, , listField] = CORRECTION_FIELDS.find(([key]) => key === field);
    let newValue = value;
    if (listField) {
      try { newValue = JSON.parse(value); } catch { setError('Dữ liệu danh sách phải là JSON hợp lệ.'); return; }
      if (!Array.isArray(newValue)) { setError('Dữ liệu danh sách phải là một mảng.'); return; }
    }
    setSaving(true);
    try {
      await correctCandidateData(detail.application_id, detail.application_version, {
        field_path: field, new_value: newValue, reason,
      });
      setReason('');
      await onCorrected();
    } catch (failure) {
      setError(failure.message || 'Không thể lưu hiệu chỉnh.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <details className="correction-panel">
      <summary><FilePenLine size={15} /> Hiệu chỉnh dữ liệu AI</summary>
      <form onSubmit={submit}>
        <label>Trường dữ liệu<select value={field} onChange={(event) => changeField(event.target.value)}>{CORRECTION_FIELDS.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
        <label>Giá trị đã xác minh<textarea value={value} onChange={(event) => setValue(event.target.value)} /></label>
        <label>Lý do hiệu chỉnh<input value={reason} minLength={3} required onChange={(event) => setReason(event.target.value)} placeholder="Ví dụ: Đã đối chiếu trực tiếp trên CV" /></label>
        {error && <p className="correction-panel__error">{error}</p>}
        <button type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu và đánh dấu cần chạy lại'}</button>
      </form>
    </details>
  );
}

function CandidateReviewContent({ detail, onDecisionUpdated }) {
  const evaluation = detail.evaluation;
  const [page, setPage] = useState(null);
  const [revealed, setRevealed] = useState(detail.privacy_mode !== 'BLIND');
  const baseResumeUrl = getOriginalResumeUrl(detail.application_id, detail.privacy_mode === 'BLIND' && revealed);
  const resumeUrl = `${baseResumeUrl}${page ? `#page=${page}` : ''}`;

  return (
    <div className="candidate-review__body">
      <section className="candidate-review__resume" aria-label="CV gốc">
        {detail.privacy_mode === 'BLIND' && !revealed ? <div className="blind-review-lock">
          <ShieldCheck size={28} />
          <strong>Danh tính và CV gốc đang được khóa</strong>
          <p>Hãy đánh giá điểm số và bằng chứng đã che trước. Thao tác mở CV sẽ được ghi vào nhật ký audit.</p>
          <button type="button" onClick={() => setRevealed(true)}>Mở danh tính và CV gốc</button>
        </div> : <>
          <div className="candidate-review__section-heading">
            <div><FileText size={17} /><strong>{detail.privacy_mode === 'BLIND' ? 'CV đã mở có audit' : 'CV gốc'}</strong></div>
            <a href={resumeUrl} target="_blank" rel="noreferrer">Mở tab mới <ExternalLink size={13} /></a>
          </div>
          <iframe key={page || 'initial'} title={`CV của ${detail.candidate_name}`} src={resumeUrl} />
        </>}
      </section>

      <section className="candidate-review__analysis" aria-label="Đánh giá theo tiêu chí">
        <div className="candidate-review__summary">
          <div><span>Điểm đã xác minh</span><strong>{evaluation ? `${evaluation.overall_score}%` : '—'}</strong></div>
          <div><span>Khoảng có thể</span><strong>{evaluation ? `${evaluation.overall_score}–${evaluation.maximum_possible_score ?? evaluation.overall_score}%` : '—'}</strong></div>
          <div><span>Độ phủ bằng chứng</span><strong>{evaluation ? `${evaluation.evidence_coverage ?? 0}%` : '—'}</strong></div>
          <div><span>Cổng bắt buộc</span><strong>{evaluation?.mandatory_gate || 'Chưa đánh giá'}</strong></div>
        </div>

        <DecisionPanel applicationId={detail.application_id} version={detail.application_version} currentStage={detail.pipeline_stage} onUpdated={onDecisionUpdated} />

        {detail.evaluation_stale && <div className="candidate-review__stale"><AlertCircle size={16} /><span><strong>Kết quả cần chạy lại.</strong> {detail.stale_reason}</span></div>}
        <CorrectionPanel detail={detail} onCorrected={onDecisionUpdated} />

        {!evaluation ? (
          <div className="workspace-state workspace-state--stacked">
            <HelpCircle size={22} />
            <strong>Chưa có lần đánh giá chính thức</strong>
            <p>Hãy chạy sàng lọc để tạo điểm và bằng chứng theo bộ tiêu chí đang áp dụng.</p>
          </div>
        ) : (
          <div className="criterion-matrix">
            <div className="candidate-review__section-heading">
              <div><ShieldCheck size={17} /><strong>Ma trận tiêu chí &amp; bằng chứng</strong></div>
              <span>{evaluation.criterion_results.length} tiêu chí</span>
            </div>
            {evaluation.criterion_results.map((criterion) => (
              <article className="criterion-evidence" key={criterion.id}>
                <div className="criterion-evidence__heading">
                  <div>
                    <span className={`criterion-importance is-${criterion.importance.toLowerCase()}`}>{criterion.importance}</span>
                    <h4>{criterion.label}</h4>
                  </div>
                  <ResultBadge result={criterion.result} />
                </div>
                <p>{criterion.explanation}</p>
                {criterion.evidence.length ? criterion.evidence.map((evidence) => (
                  <button
                    className="criterion-evidence__source"
                    key={evidence.id}
                    type="button"
                    onClick={() => evidence.page_number && setPage(evidence.page_number)}
                    disabled={!evidence.page_number}
                    title={evidence.page_number ? `Mở trang ${evidence.page_number} trong CV` : 'Không xác định được trang nguồn'}
                  >
                    <span>“{evidence.excerpt}”</span>
                    <footer>
                      {evidence.page_number ? <><LocateFixed size={12} /> Trang {evidence.page_number} · bấm để kiểm chứng · </> : 'Chưa xác định trang · dùng tìm kiếm trong CV · '}
                      Độ tin cậy {Math.round(evidence.confidence * 100)}%
                    </footer>
                  </button>
                )) : (
                  <div className="criterion-evidence__missing">
                    <HelpCircle size={15} /> Không tìm thấy bằng chứng trực tiếp trong CV — cần người tuyển dụng xác minh.
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default function CandidateReviewDrawer({ candidate, onClose }) {
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(Boolean(candidate?.application_id));
  const applicationId = candidate?.application_id;
  const title = useMemo(() => detail?.candidate_name || candidate?.candidate_name || 'Hồ sơ ứng viên', [candidate, detail]);

  useEffect(() => {
    const onKeyDown = (event) => event.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  const loadDetail = () => {
    setLoading(true);
    setError('');
    return fetchCandidateDetail(applicationId)
      .then(setDetail)
      .catch((reason) => setError(reason.message || 'Không thể tải hồ sơ ứng viên.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    let active = true;
    if (!applicationId) {
      setLoading(false);
      setError('Hồ sơ này được tạo trước bản nâng cấp. Hãy chạy lại sàng lọc để liên kết CV với bản đánh giá có bằng chứng.');
      return () => { active = false; };
    }
    fetchCandidateDetail(applicationId)
      .then((value) => active && setDetail(value))
      .catch((reason) => active && setError(reason.message || 'Không thể tải hồ sơ ứng viên.'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [applicationId]);

  return createPortal(
    <div className="candidate-review-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <aside className="candidate-review" role="dialog" aria-modal="true" aria-label={`Đánh giá hồ sơ ${title}`}>
        <header className="candidate-review__header">
          <div>
            <span className="section-eyebrow">Hồ sơ đánh giá</span>
            <h2>{title}</h2>
            <p>{detail?.candidate_email || candidate?.candidate_email || detail?.file_name || candidate?.candidate_file_name}</p>
          </div>
          <button className="candidate-review__close" type="button" onClick={onClose} aria-label="Đóng hồ sơ"><X size={20} /></button>
        </header>

        {loading && <div className="workspace-state workspace-state--stacked candidate-review__state"><LoaderCircle className="workspace-state__spin" /><strong>Đang tải hồ sơ và bằng chứng…</strong></div>}
        {!loading && error && <div className="workspace-state workspace-state--stacked workspace-state--error candidate-review__state"><AlertCircle /><strong>Chưa thể hiển thị bản đánh giá</strong><p>{error}</p></div>}
        {!loading && !error && detail && <CandidateReviewContent detail={detail} onDecisionUpdated={loadDetail} />}
      </aside>
    </div>,
    document.body,
  );
}
