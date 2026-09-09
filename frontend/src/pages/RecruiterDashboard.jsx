import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Play, RefreshCw, Sliders, Edit3, Trash2, FileText, CheckCircle2, XCircle, Target } from 'lucide-react';
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

  // Compute KPI metrics
  const totalResumes = candidates.length;
  const shortlistedCount = candidates.filter(c => c.recruiter_status === 'SHORTLISTED' || c.recruiter_status === 'INTERVIEW').length;
  const rejectedCount = candidates.filter(c => c.recruiter_status === 'REJECTED').length;
  const avgScore = candidates.length > 0
    ? Math.round(candidates.reduce((acc, c) => acc + (c.overall_score || 0), 0) / candidates.length * 10) / 10
    : 0;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* ROW 1: ENTERPRISE KPI STATS SUMMARY CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        
        <div className="kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <FileText size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600 }}>TỔNG SỐ CV</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{totalResumes} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 400 }}>Hồ sơ</span></div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600 }}>ĐƯỢC CHỌN LỌC</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34d399' }}>
              {shortlistedCount} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 400 }}>({totalResumes > 0 ? Math.round(shortlistedCount / totalResumes * 100) : 0}%)</span>
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(244, 63, 94, 0.15)', color: '#f87171' }}>
            <XCircle size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600 }}>ĐÃ LOẠI</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f87171' }}>
              {rejectedCount} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 400 }}>({totalResumes > 0 ? Math.round(rejectedCount / totalResumes * 100) : 0}%)</span>
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8' }}>
            <Target size={22} />
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600 }}>ĐIỂM MATCH TRUNG BÌNH</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#38bdf8' }}>{avgScore}%</div>
          </div>
        </div>

      </div>

      {/* ROW 2: COMBINED AI CONTROL CARD */}
      <div className="glass-panel" style={{ padding: '24px', background: 'rgba(18, 24, 38, 0.85)', border: '1px solid var(--border-glow)' }}>
        
        {/* Step Header: Job Selection */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '18px', borderBottom: '1px solid var(--border-color)', marginBottom: '20px' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-primary)' }}>
              <Briefcase size={20} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>BƯỚC 1: CHỌN VỊ TRÍ TUYỂN DỤNG</label>
              <select
                className="select-field"
                value={selectedJob?.id || ''}
                onChange={(e) => {
                  const j = jobs.find((item) => item.id === e.target.value);
                  if (j) selectJob(j);
                }}
                style={{ fontWeight: 800, fontSize: '1rem', minWidth: '280px', marginTop: '2px' }}
              >
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} ({j.department || 'Chung'})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Job Action Buttons */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                setEditingJob(null);
                setShowJobForm(true);
              }}
              className="btn btn-secondary"
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
                >
                  <Edit3 size={16} /> Sửa Yêu cầu
                </button>

                <button
                  onClick={handleDeleteJob}
                  className="btn btn-secondary"
                  style={{ color: 'var(--accent-rose)', borderColor: 'rgba(244, 63, 94, 0.3)' }}
                >
                  <Trash2 size={16} /> Xóa
                </button>
              </>
            )}
          </div>
        </div>

        {/* Step Body: Sliders + Embedded Upload Zone */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', alignItems: 'center' }}>
          
          {/* Section A: Live Criterion Weight Adjusters */}
          <div style={{ background: 'rgba(0,0,0,0.25)', padding: '16px 20px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem' }}>
              <Sliders size={16} /> BƯỚC 2: TỰ ĐIỀU CHỈNH TRỌNG SỐ AI
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.85rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Kỹ năng chuyên môn:</span>
                  <b style={{ color: 'var(--accent-cyan)' }}>{Math.round(sliderWeights.wSkills * 100)}%</b>
                </div>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wSkills}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wSkills: parseFloat(e.target.value) }))}
                  style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Kinh nghiệm làm việc:</span>
                  <b style={{ color: 'var(--accent-primary)' }}>{Math.round(sliderWeights.wExp * 100)}%</b>
                </div>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wExp}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wExp: parseFloat(e.target.value) }))}
                  style={{ width: '100%', accentColor: 'var(--accent-primary)' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Học vấn & Bằng cấp:</span>
                  <b style={{ color: '#a855f7' }}>{Math.round(sliderWeights.wEdu * 100)}%</b>
                </div>
                <input
                  type="range" min="0" max="1" step="0.05"
                  value={sliderWeights.wEdu}
                  onChange={(e) => setSliderWeights(prev => ({ ...prev, wEdu: parseFloat(e.target.value) }))}
                  style={{ width: '100%', accentColor: '#a855f7' }}
                />
              </div>
            </div>
          </div>

          {/* Section B: Integrated PDF Resume Bulk Uploader */}
          <div style={{ flex: '1' }}>
            <ResumeUploader jobId={selectedJob?.id} onResumesUploaded={() => selectedJob && loadScreenings(selectedJob.id)} />
          </div>

        </div>

        {/* Big Glow Primary Action Button */}
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={handleRunScreening}
            className="btn btn-primary"
            disabled={!selectedJob || screeningLoading}
            style={{
              padding: '14px 32px',
              fontSize: '1.05rem',
              fontWeight: 800,
              borderRadius: '12px',
              boxShadow: '0 8px 25px rgba(99, 102, 241, 0.4)'
            }}
          >
            {screeningLoading ? <RefreshCw size={20} className="spin" /> : <Play size={20} />}
            BƯỚC 3: CHẠY ĐỘNG CƠ KHỚP NỐI AI
          </button>
        </div>

      </div>

      {/* ROW 3: DYNAMIC CANDIDATE RANKING TABLE & EXPORT PANEL */}
      <div>
        {selectedJob && <ExportFeedbackPanel selectedJobId={selectedJob.id} candidateCount={candidates.length} />}

        <CandidateTable
          candidates={candidates}
          jobWeights={sliderWeights}
          onSelectCandidate={(c) => setSelectedCandidate(c)}
          onStatusChange={(updated) => {
            setCandidates(prev => prev.map(c => c.id === updated.id ? updated : c));
          }}
        />
      </div>

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
