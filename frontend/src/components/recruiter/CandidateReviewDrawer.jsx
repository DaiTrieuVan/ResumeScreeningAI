import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle, CheckCircle2, ExternalLink, FileText, HelpCircle,
  LoaderCircle, ShieldCheck, X, XCircle,
} from 'lucide-react';

import { fetchCandidateDetail, getOriginalResumeUrl } from '../../services/recruiterApi';

const RESULT_META = {
  MET: { label: 'Đạt', icon: CheckCircle2, className: 'is-met' },
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

function CandidateReviewContent({ detail }) {
  const evaluation = detail.evaluation;
  const resumeUrl = getOriginalResumeUrl(detail.application_id);

  return (
    <div className="candidate-review__body">
      <section className="candidate-review__resume" aria-label="CV gốc">
        <div className="candidate-review__section-heading">
          <div><FileText size={17} /><strong>CV gốc</strong></div>
          <a href={resumeUrl} target="_blank" rel="noreferrer">Mở tab mới <ExternalLink size={13} /></a>
        </div>
        <iframe title={`CV của ${detail.candidate_name}`} src={resumeUrl} />
      </section>

      <section className="candidate-review__analysis" aria-label="Đánh giá theo tiêu chí">
        <div className="candidate-review__summary">
          <div><span>Điểm chính thức</span><strong>{evaluation ? `${evaluation.overall_score}%` : '—'}</strong></div>
          <div><span>Cổng bắt buộc</span><strong>{evaluation?.mandatory_gate || 'Chưa đánh giá'}</strong></div>
          <div><span>Trạng thái bằng chứng</span><strong>{evaluation?.evidence_status || 'Chưa có'}</strong></div>
        </div>

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
                  <blockquote key={evidence.id}>
                    “{evidence.excerpt}”
                    <footer>
                      {evidence.page_number ? `Trang ${evidence.page_number} · ` : ''}
                      Độ tin cậy {Math.round(evidence.confidence * 100)}%
                    </footer>
                  </blockquote>
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

  useEffect(() => {
    let active = true;
    if (!applicationId) {
      setLoading(false);
      setError('Hồ sơ này được tạo trước bản nâng cấp. Hãy chạy lại sàng lọc để liên kết CV với bản đánh giá có bằng chứng.');
      return () => { active = false; };
    }
    setLoading(true);
    setError('');
    fetchCandidateDetail(applicationId)
      .then((value) => active && setDetail(value))
      .catch((reason) => active && setError(reason.message || 'Không thể tải hồ sơ ứng viên.'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [applicationId]);

  return (
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
        {!loading && !error && detail && <CandidateReviewContent detail={detail} />}
      </aside>
    </div>
  );
}
