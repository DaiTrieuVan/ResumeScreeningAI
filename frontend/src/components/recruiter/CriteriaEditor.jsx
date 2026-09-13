import React, { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, Save, Sliders, TriangleAlert } from 'lucide-react';

import { createCriteriaSet, fetchCriteriaSets, publishCriteriaSet } from '../../services/recruiterApi';
import { WorkspaceError, WorkspaceLoading } from './WorkspaceStates';


const toPercentages = (weights) => ({
  skills: Math.round((weights?.skills ?? 0.5) * 100),
  experience: Math.round((weights?.experience ?? 0.35) * 100),
  education: Math.round((weights?.education ?? 0.15) * 100),
});

const toApiWeights = (weights) => Object.fromEntries(
  Object.entries(weights).map(([key, value]) => [key, value / 100]),
);

function legacyCriteria(job) {
  const criteria = (job.required_skills || []).map((skill, index) => ({
    category: 'SKILL', importance: 'MANDATORY', label: skill,
    operator: 'CONTAINS_ANY', expected_value: [skill], weight: 0, sort_order: index,
  }));
  if (job.min_years_experience) {
    criteria.push({
      category: 'EXPERIENCE', importance: 'MANDATORY',
      label: `Tối thiểu ${job.min_years_experience} năm kinh nghiệm`,
      operator: 'MIN_VALUE', expected_value: job.min_years_experience,
      weight: 0, sort_order: criteria.length,
    });
  }
  if (job.required_education) {
    criteria.push({
      category: 'EDUCATION', importance: 'PREFERRED', label: job.required_education,
      operator: 'EQUALS', expected_value: job.required_education,
      weight: 0, sort_order: criteria.length,
    });
  }
  return criteria;
}

export default function CriteriaEditor({ job, onWeightsChange, onPublished }) {
  const fallbackWeights = useMemo(() => ({
    skills: job?.weight_skills ?? 0.5,
    experience: job?.weight_experience ?? 0.35,
    education: job?.weight_education ?? 0.15,
  }), [job]);
  const [criteriaSets, setCriteriaSets] = useState([]);
  const [weights, setWeights] = useState(() => toPercentages(fallbackWeights));
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const activeSet = criteriaSets.find((item) => item.status === 'PUBLISHED');
  const officialWeights = activeSet?.scoring_weights || fallbackWeights;
  const total = Object.values(weights).reduce((sum, value) => sum + value, 0);
  const dirty = Object.entries(weights).some(
    ([key, value]) => value !== Math.round((officialWeights[key] || 0) * 100),
  );

  const loadCriteria = async () => {
    if (!job?.id) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchCriteriaSets(job.id);
      setCriteriaSets(data);
      const published = data.find((item) => item.status === 'PUBLISHED');
      setWeights(toPercentages(published?.scoring_weights || fallbackWeights));
    } catch (requestError) {
      setError(requestError.message);
      setWeights(toPercentages(fallbackWeights));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCriteria(); }, [job?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    onWeightsChange?.({
      wSkills: weights.skills / 100,
      wExp: weights.experience / 100,
      wEdu: weights.education / 100,
    }, dirty);
  }, [weights, dirty]); // eslint-disable-line react-hooks/exhaustive-deps

  const saveVersion = async () => {
    if (total !== 100 || !dirty) return;
    setSaving(true);
    setError('');
    try {
      const copiedCriteria = (activeSet?.criteria || legacyCriteria(job)).map(({ id, ...item }) => item);
      const draft = await createCriteriaSet(job.id, {
        name: `Bộ tiêu chí v${(criteriaSets[0]?.version_number || 0) + 1}`,
        scoring_weights: toApiWeights(weights),
        criteria: copiedCriteria,
      });
      const published = await publishCriteriaSet(draft.id, job.version || 1);
      setCriteriaSets((current) => [
        published,
        ...current.map((item) => item.status === 'PUBLISHED' ? { ...item, status: 'RETIRED' } : item),
      ]);
      onPublished?.(published);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <WorkspaceLoading label="Đang tải bộ tiêu chí…" />;

  return (
    <section className="criteria-editor" aria-label="Cấu hình trọng số sàng lọc">
      <div className="criteria-editor__header">
        <div>
          <span className="section-eyebrow"><Sliders size={15} /> Bộ tiêu chí đánh giá</span>
          <h3>{activeSet ? `Phiên bản ${activeSet.version_number} · Đang áp dụng` : 'Tiêu chí mặc định'}</h3>
        </div>
        <span className="criteria-editor__official"><CheckCircle2 size={14} /> Điểm chính thức</span>
      </div>

      {error && <WorkspaceError message={error} onRetry={loadCriteria} />}

      <div className="criteria-editor__weights">
        {[
          ['skills', 'Kỹ năng chuyên môn'],
          ['experience', 'Kinh nghiệm làm việc'],
          ['education', 'Học vấn & bằng cấp'],
        ].map(([key, label]) => (
          <label key={key} className="criteria-weight">
            <span>{label}<b>{weights[key]}%</b></span>
            <input
              type="range" min="0" max="100" step="5" value={weights[key]}
              onChange={(event) => setWeights((current) => ({ ...current, [key]: Number(event.target.value) }))}
            />
          </label>
        ))}
      </div>

      <div className={`criteria-editor__summary ${total === 100 ? 'is-valid' : 'is-invalid'}`}>
        {total === 100 ? <CheckCircle2 size={16} /> : <TriangleAlert size={16} />}
        <span>Tổng trọng số: <strong>{total}%</strong>{total !== 100 && ` · ${total < 100 ? 'Thiếu' : 'Vượt'} ${Math.abs(100 - total)}%`}</span>
        <button type="button" className="btn btn-primary" onClick={saveVersion} disabled={!dirty || total !== 100 || saving}>
          <Save size={15} /> {saving ? 'Đang lưu…' : 'Lưu thành phiên bản mới'}
        </button>
      </div>

      {dirty && (
        <p className="criteria-editor__simulation">
          Bạn đang xem điểm mô phỏng. Điểm chính thức và shortlist sẽ không đổi trước khi lưu rồi chạy đánh giá lại.
        </p>
      )}
    </section>
  );
}
