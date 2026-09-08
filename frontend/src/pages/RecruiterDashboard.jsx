import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Play, RefreshCw, Sliders, Edit3, Trash2 } from 'lucide-react';
import { fetchJobs, triggerScreeningStream, fetchJobScreenings, deleteJob } from '../services/api';
import JobPostingForm from '../components/JobPostingForm';
import ResumeUploader from '../components/ResumeUploader';
import CandidateTable from '../components/CandidateTable';
import CandidateDetailModal from '../components/CandidateDetailModal';
import ExportFeedbackPanel from '../components/ExportFeedbackPanel';
import ScreeningProgressModal from '../components/ScreeningProgressModal';

export default function RecruiterDashboard() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  
  const [showJobForm, setShowJobForm] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [screeningLoading, setScreeningLoading] = useState(false);

  // Live Progress Modal State
  const [progressModalOpen, setProgressModalOpen] = useState(false);
  const [screeningProgressData, setScreeningProgressData] = useState(null);
  const [screeningLogs, setScreeningLogs] = useState([]);
  const [screeningCompleted, setScreeningCompleted] = useState(false);
  const [screeningError, setScreeningError] = useState(null);

  // Live Slider Weights for selected job
  const [sliderWeights, setSliderWeights] = useState({ wSkills: 0.5, wExp: 0.35, wEdu: 0.15 });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await fetchJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJob) {
        selectJob(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectJob = async (job) => {
    setSelectedJob(job);
    if (job) {
      setSliderWeights({
        wSkills: job.weight_skills ?? 0.5,
        wExp: job.weight_experience ?? 0.35,
        wEdu: job.weight_education ?? 0.15,
      });
      loadScreenings(job.id);
    }
  };

  const loadScreenings = async (jobId) => {
    try {
      const data = await fetchJobScreenings(jobId);
      setCandidates(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunScreening = async () => {
    if (!selectedJob) return;

    setScreeningLoading(true);
    setProgressModalOpen(true);
    setScreeningCompleted(false);
    setScreeningError(null);

    const startTime = new Date().toLocaleTimeString();
    setScreeningLogs([{ time: startTime, text: `Bắt đầu phân tích & sàng lọc cho vị trí: ${selectedJob.title}` }]);

    try {
      const results = await triggerScreeningStream(
        selectedJob.id,
        null,
        (payload) => {
          setScreeningProgressData(payload);

          const time = new Date().toLocaleTimeString();
          if (payload.stage === 'stage1_vector') {
            setScreeningLogs((prev) => [
              ...prev,
              { time, text: payload.message || `Đang chạy khớp nối Vector Similarity cho ${payload.total} ứng viên...` }
            ]);
          } else if (payload.stage === 'stage1_vector_done') {
            const llmCount = payload.llm_candidates || payload.total;
            const skippedCount = payload.skipped_candidates || 0;
            setScreeningLogs((prev) => [
              ...prev,
              { time, text: `Vector Similarity hoàn tất.` },
              { time, text: `Top-K Filter: ${llmCount} ứng viên đủ điều kiện → LLM | ${skippedCount} ứng viên bỏ qua` },
              { time, text: `Bắt đầu LLM song song (${payload.message?.match(/\d+ luồng/)?.[0] || '5 luồng'})...` }
            ]);
          } else if (payload.stage === 'stage2_llm') {
            const currentName = payload.current_candidate || payload.current_candidate_name || `Ứng viên #${payload.current}`;
            setScreeningLogs((prev) => [
              ...prev,
              { time, text: `[${payload.current}/${payload.total}] Đã đánh giá AI: ${currentName}` }
            ]);
          }
        }
      );
      setCandidates(results);
      setScreeningCompleted(true);
      const finishTime = new Date().toLocaleTimeString();
      setScreeningLogs((prev) => [...prev, { time: finishTime, text: 'Đã hoàn tất đánh giá toàn bộ CV thành công!' }]);
    } catch (err) {
      setScreeningError(err.message || 'Lỗi xảy ra trong quá trình sàng lọc AI.');
      const errTime = new Date().toLocaleTimeString();
      setScreeningLogs((prev) => [...prev, { time: errTime, text: `LỖI: ${err.message}` }]);
    } finally {
      setScreeningLoading(false);
    }
  };

  const handleJobSaved = (savedJob) => {
    if (editingJob) {
      setJobs((prev) => prev.map((j) => (j.id === savedJob.id ? savedJob : j)));
      setSelectedJob(savedJob);
    } else {
      setJobs((prev) => [savedJob, ...prev]);
      selectJob(savedJob);
    }
    setEditingJob(null);
    setShowJobForm(false);
  };

  const handleDeleteJob = async () => {
    if (!selectedJob) return;
    const confirmDelete = window.confirm(`Bạn có chắc chắn muốn xóa vị trí tuyển dụng "${selectedJob.title}"? Tất cả kết quả đánh giá liên quan sẽ bị xóa.`);
    if (!confirmDelete) return;

    try {
      await deleteJob(selectedJob.id);
      const updated = jobs.filter((j) => j.id !== selectedJob.id);
      setJobs(updated);
      if (updated.length > 0) {
        selectJob(updated[0]);
      } else {
        setSelectedJob(null);
        setCandidates([]);
      }
    } catch (err) {
      alert('Lỗi xóa vị trí tuyển dụng: ' + err.message);
    }
  };

  return (
    <div className="animate-fade-in">
      
      {/* Top Header Controls */}
      <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '24px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Job Selection Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Briefcase color="var(--accent-primary)" size={20} />
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>Vị trí Tuyển dụng Hiện tại</label>
            <select
              className="select-field"
              value={selectedJob?.id || ''}
              onChange={(e) => {
                const j = jobs.find((item) => item.id === e.target.value);
                if (j) selectJob(j);
              }}
              style={{ fontWeight: 700, fontSize: '0.95rem', minWidth: '260px' }}
            >
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} ({j.department || 'Chung'})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => {
              setEditingJob(null);
              setShowJobForm(true);
            }}
            className="btn btn-secondary"
            title="Tạo vị trí tuyển dụng mới"
          >
            <Plus size={16} /> Tạo Yêu cầu Mới
          </button>

          {selectedJob && (
            <>
              <button
                onClick={() => {
                  setEditingJob(selectedJob);
                  setShowJobForm(true);
                }}
                className="btn btn-secondary"
                style={{ padding: '8px 12px' }}
                title="Chỉnh sửa vị trí tuyển dụng đang chọn"
              >
                <Edit3 size={16} /> Sửa Yêu cầu
              </button>

              <button
                onClick={handleDeleteJob}
                className="btn btn-secondary"
                style={{ padding: '8px 12px', color: 'var(--accent-red)', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                title="Xóa vị trí tuyển dụng đang chọn"
              >
                <Trash2 size={16} /> Xóa Yêu cầu
              </button>
            </>
          )}

          <button
            onClick={handleRunScreening}
            className="btn btn-primary"
            disabled={!selectedJob || screeningLoading}
          >
            {screeningLoading ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
            Chạy Động cơ Khớp nối AI
          </button>
        </div>

      </div>

      {/* Selected Job Criteria & Live Sliders Header */}
      {selectedJob && (
        <div className="glass-panel" style={{ padding: '18px 24px', marginBottom: '24px', background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '4px' }}>{selectedJob.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Kỹ năng bắt buộc: <b>{(selectedJob.required_skills || []).join(', ')}</b> | Kinh nghiệm tối thiểu: <b>{selectedJob.min_years_experience} năm</b>
              </p>
            </div>

            {/* Live Criterion Weight Adjuster (FR-008) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.8rem', background: 'rgba(0,0,0,0.3)', padding: '10px 16px', borderRadius: '12px' }}>
              <Sliders size={16} color="var(--accent-cyan)" />
              <div>
                <span>Kỹ năng: <b>{Math.round(sliderWeights.wSkills * 100)}%</b></span>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wSkills}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wSkills: parseFloat(e.target.value) }))}
                  style={{ display: 'block', width: '90px' }}
                />
              </div>
              <div>
                <span>Kinh nghiệm: <b>{Math.round(sliderWeights.wExp * 100)}%</b></span>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wExp}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wExp: parseFloat(e.target.value) }))}
                  style={{ display: 'block', width: '90px' }}
                />
              </div>
              <div>
                <span>Học vấn: <b>{Math.round(sliderWeights.wEdu * 100)}%</b></span>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wEdu}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wEdu: parseFloat(e.target.value) }))}
                  style={{ display: 'block', width: '90px' }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PDF Bulk Uploader */}
      <ResumeUploader jobId={selectedJob?.id} onResumesUploaded={() => selectedJob && loadScreenings(selectedJob.id)} />

      {/* Export Panel */}
      {selectedJob && <ExportFeedbackPanel selectedJobId={selectedJob.id} candidateCount={candidates.length} />}

      {/* Candidate Table */}
      <CandidateTable
        candidates={candidates}
        jobWeights={sliderWeights}
        onSelectCandidate={(c) => setSelectedCandidate(c)}
        onStatusChange={(updated) => {
          setCandidates(prev => prev.map(c => c.id === updated.id ? updated : c));
        }}
      />

      {/* Modals */}
      {showJobForm && (
        <JobPostingForm
          initialData={editingJob}
          onJobSaved={handleJobSaved}
          onClose={() => {
            setShowJobForm(false);
            setEditingJob(null);
          }}
        />
      )}

      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}

      <ScreeningProgressModal
        isOpen={progressModalOpen}
        progressData={screeningProgressData}
        logs={screeningLogs}
        isCompleted={screeningCompleted}
        error={screeningError}
        onClose={() => setProgressModalOpen(false)}
      />

    </div>
  );
}
