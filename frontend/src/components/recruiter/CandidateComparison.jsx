import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { AlertCircle, CheckCircle2, HelpCircle, Scale, X, XCircle } from 'lucide-react';

import { compareJobCandidates } from '../../services/recruiterApi';

const STATES = {
  MET: ['Đạt', CheckCircle2, 'is-met'], NOT_MET: ['Chưa đạt', XCircle, 'is-not-met'],
  UNKNOWN: ['Chưa đủ dữ liệu', HelpCircle, 'is-unknown'], NOT_APPLICABLE: ['Không áp dụng', AlertCircle, 'is-na'],
};

function Outcome({ value }) {
  const [label, Icon, className] = STATES[value] || STATES.UNKNOWN;
  return <span className={`evidence-result ${className}`}><Icon size={13} /> {label}</span>;
}

export default function CandidateComparison({ jobId, applicationIds, criteriaSetId, onClose }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { compareJobCandidates(jobId, applicationIds, criteriaSetId).then(setData).catch((reason) => setError(reason.message)); }, [jobId, applicationIds, criteriaSetId]);
  useEffect(() => { const close = (event) => event.key === 'Escape' && onClose(); document.addEventListener('keydown', close); return () => document.removeEventListener('keydown', close); }, [onClose]);

  return createPortal(<div className="comparison-backdrop"><section className="candidate-comparison" role="dialog" aria-modal="true" aria-label="So sánh ứng viên">
    <header><div><span className="section-eyebrow"><Scale size={15} /> So sánh finalist</span><h2>Đặt ứng viên cạnh nhau, không dựa vào trí nhớ</h2><p>Mọi kết quả dùng cùng phiên bản tiêu chí {data?.criteria_version || ''}.</p></div><button aria-label="Đóng so sánh" onClick={onClose}><X /></button></header>
    {!data && !error && <div className="workspace-state">Đang dựng ma trận so sánh…</div>}
    {error && <div className="workspace-state workspace-state--error">{error}</div>}
    {data && <div className="comparison-table"><table><thead><tr><th>Tiêu chí</th>{data.candidates.map((candidate) => <th key={candidate.application_id}><strong>{candidate.candidate_name}</strong><span>{candidate.overall_score}% · {candidate.pipeline_stage}</span></th>)}</tr></thead><tbody><tr className="comparison-gate"><th>Cổng bắt buộc</th>{data.candidates.map((candidate) => <td key={candidate.application_id}>{candidate.mandatory_gate}</td>)}</tr>{data.criteria.map((criterion) => <tr key={criterion.criterion_id}><th><span>{criterion.importance}</span><strong>{criterion.label}</strong></th>{data.candidates.map((candidate) => { const result = criterion.results[candidate.application_id]; return <td key={candidate.application_id}>{result ? <><Outcome value={result.result} /><p>{result.explanation}</p>{result.evidence?.[0] && <blockquote>“{result.evidence[0].excerpt}”</blockquote>}</> : <Outcome value="UNKNOWN" />}</td>; })}</tr>)}</tbody></table></div>}
  </section></div>, document.body);
}
