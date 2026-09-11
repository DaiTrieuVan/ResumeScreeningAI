import React, { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Columns3, Eye, Filter, Search } from 'lucide-react';
import { queryJobCandidates, saveCandidateView } from '../../services/recruiterApi';
import BulkActionBar from './BulkActionBar';

const DEFAULT_COLUMNS = ['candidate', 'score', 'gate', 'stage'];
const STAGES = { RECEIVED: 'Mới nhận', AI_ANALYZED: 'AI đã phân tích', RECRUITER_REVIEW: 'Đang xem', SHORTLISTED: 'Shortlist', HR_INTERVIEW: 'PV nhân sự', TECH_INTERVIEW: 'PV chuyên môn', OFFER: 'Đề nghị', HIRED: 'Đã tuyển', REJECTED: 'Từ chối' };

export default function CandidateGrid({ jobId, refreshToken, onSelectCandidate }) {
  const storageKey = `recruiter-grid:${jobId}`;
  const stored = (() => { try { return JSON.parse(localStorage.getItem(storageKey)) || {}; } catch { return {}; } })();
  const [query, setQuery] = useState(stored.query || '');
  const [stage, setStage] = useState(stored.stage || '');
  const [minScore, setMinScore] = useState(stored.minScore || 0);
  const [sort, setSort] = useState(stored.sort || 'score_desc');
  const [page, setPage] = useState(1);
  const [columns, setColumns] = useState(stored.columns || DEFAULT_COLUMNS);
  const [data, setData] = useState({ items: [], total: 0, page_size: 25 });
  const [selected, setSelected] = useState(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  const params = useMemo(() => ({ q: query, stage: stage ? [stage] : [], min_score: minScore, sort, page, page_size: 25 }), [query, stage, minScore, sort, page]);
  useEffect(() => { localStorage.setItem(storageKey, JSON.stringify({ query, stage, minScore, sort, columns })); }, [storageKey, query, stage, minScore, sort, columns]);
  useEffect(() => {
    let active = true; const timer = setTimeout(() => {
      setLoading(true); setError('');
      queryJobCandidates(jobId, params).then((value) => active && setData(value)).catch((reason) => active && setError(reason.message)).finally(() => active && setLoading(false));
    }, 180);
    return () => { active = false; clearTimeout(timer); };
  }, [jobId, params, refreshToken, reloadKey]);
  useEffect(() => setPage(1), [query, stage, minScore, sort]);

  const pageCount = Math.max(1, Math.ceil(data.total / data.page_size));
  const toggle = (item) => setSelected((current) => { const next = new Map(current); next.has(item.application_id) ? next.delete(item.application_id) : next.set(item.application_id, item.version); return next; });
  const selectedIds = [...selected.keys()];
  const versions = Object.fromEntries(selected);
  const has = (name) => columns.includes(name);
  const toggleColumn = (name) => setColumns((current) => current.includes(name) ? current.filter((value) => value !== name) : [...current, name]);

  return <div className="glass-panel candidate-grid">
    <div className="panel-heading"><div><span className="section-eyebrow">Danh sách ứng viên</span><h3>{data.total} hồ sơ trong chế độ xem</h3></div><details className="column-chooser"><summary><Columns3 size={15} /> Cột hiển thị</summary><div>{DEFAULT_COLUMNS.map((column) => <label key={column}><input type="checkbox" checked={has(column)} onChange={() => toggleColumn(column)} /> {column}</label>)}<button onClick={() => saveCandidateView(jobId, { name: `Chế độ xem ${new Date().toLocaleDateString('vi-VN')}`, columns, filters: { q: query, stage, min_score: minScore }, sort })}>Lưu chế độ xem</button></div></details></div>
    <div className="candidate-grid__filters">
      <label><Search size={15} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Tên, email hoặc kỹ năng…" /></label>
      <label><Filter size={15} /><select value={stage} onChange={(e) => setStage(e.target.value)}><option value="">Mọi giai đoạn</option>{Object.entries(STAGES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <label>Điểm từ <input type="number" min="0" max="100" value={minScore} onChange={(e) => setMinScore(Number(e.target.value))} /></label>
      <select value={sort} onChange={(e) => setSort(e.target.value)}><option value="score_desc">Điểm cao trước</option><option value="score_asc">Điểm thấp trước</option><option value="received_desc">Mới nhận trước</option><option value="risk_desc">Rủi ro trước</option></select>
    </div>
    <BulkActionBar jobId={jobId} selected={selectedIds} versions={versions} onClear={() => setSelected(new Map())} onCompleted={() => { setSelected(new Map()); setPage(1); setReloadKey((value) => value + 1); }} />
    {loading ? <div className="workspace-state">Đang tải danh sách…</div> : error ? <div className="workspace-state workspace-state--error">{error}</div> : <div className="candidate-grid__table"><table><thead><tr><th><input type="checkbox" aria-label="Chọn trang hiện tại" checked={data.items.length > 0 && data.items.every((item) => selected.has(item.application_id))} onChange={() => setSelected((current) => { const next = new Map(current); const all = data.items.every((item) => next.has(item.application_id)); data.items.forEach((item) => all ? next.delete(item.application_id) : next.set(item.application_id, item.version)); return next; })} /></th>{has('candidate') && <th>Ứng viên</th>}{has('score') && <th>Điểm</th>}{has('gate') && <th>Tiêu chí bắt buộc</th>}{has('stage') && <th>Giai đoạn</th>}<th /></tr></thead><tbody>{data.items.map((item) => <tr key={item.application_id}><td><input type="checkbox" checked={selected.has(item.application_id)} onChange={() => toggle(item)} /></td>{has('candidate') && <td><strong>{item.candidate_name}</strong><span>{item.candidate_email || item.file_name}</span></td>}{has('score') && <td><span className="score-pill score-high">{item.score == null ? '—' : `${item.score}%`}</span></td>}{has('gate') && <td><span className={`gate-pill is-${item.mandatory_gate.toLowerCase()}`}>{item.mandatory_gate}</span></td>}{has('stage') && <td>{STAGES[item.stage] || item.stage}</td>}<td><button onClick={() => onSelectCandidate(item)}><Eye size={14} /> Xem</button></td></tr>)}</tbody></table></div>}
    <div className="candidate-grid__pagination"><span>Trang {page}/{pageCount} · {selected.size} đã chọn trên nhiều trang</span><div><button disabled={page === 1} onClick={() => setPage(page - 1)}><ChevronLeft size={16} /></button><button disabled={page === pageCount} onClick={() => setPage(page + 1)}><ChevronRight size={16} /></button></div></div>
  </div>;
}
