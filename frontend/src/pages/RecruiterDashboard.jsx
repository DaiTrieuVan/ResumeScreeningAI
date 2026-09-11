import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Play, RefreshCw, Edit3, Trash2, FileText, CheckCircle2, XCircle, Target } from 'lucide-react';
import { fetchJobs, triggerScreeningStream, fetchJobScreenings, deleteJob } from '../services/api';
import JobPostingForm from '../components/JobPostingForm';
import CandidateGrid from '../components/recruiter/CandidateGrid';
import CandidateReviewDrawer from '../components/recruiter/CandidateReviewDrawer';
import ExportFeedbackPanel from '../components/ExportFeedbackPanel';
import ScreeningProgressModal from '../components/ScreeningProgressModal';
import CriteriaEditor from '../components/recruiter/CriteriaEditor';
import BatchUploader from '../components/recruiter/BatchUploader';

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
  const [isScoreSimulation, setIsScoreSimulation] = useState(false);

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
    <div className="dashboard-page animate-fade-in">
      <div className="page-heading">
        <div>
          <span className="page-kicker">Không gian tuyển dụng</span>
          <h2>Tổng quan tuyển dụng</h2>
          <p>Quản lý yêu cầu, phân tích hồ sơ và theo dõi ứng viên trong một quy trình liền mạch.</p>
        </div>
        <div className="page-heading__meta">
          <span className="status-dot" /> Hệ thống AI sẵn sàng
        </div>
      </div>
      
      {/* ROW 1: ENTERPRISE KPI STATS SUMMARY CARDS */}
      <div className="metrics-grid">
        
        <div className="kpi-card">
          <div className="kpi-icon-box kpi-icon-box--neutral">
            <FileText size={22} />
          </div>
          <div>
            <div className="kpi-label">Tổng số CV</div>
            <div className="kpi-value">{totalResumes} <span>hồ sơ</span></div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box kpi-icon-box--success">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="kpi-label">Được chọn lọc</div>
            <div className="kpi-value kpi-value--success">
              {shortlistedCount} <span>{totalResumes > 0 ? Math.round(shortlistedCount / totalResumes * 100) : 0}% tổng số</span>
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box kpi-icon-box--danger">
            <XCircle size={22} />
          </div>
          <div>
            <div className="kpi-label">Đã loại</div>
            <div className="kpi-value kpi-value--danger">
              {rejectedCount} <span>{totalResumes > 0 ? Math.round(rejectedCount / totalResumes * 100) : 0}% tổng số</span>
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-box kpi-icon-box--info">
            <Target size={22} />
          </div>
          <div>
            <div className="kpi-label">Điểm phù hợp trung bình</div>
            <div className="kpi-value kpi-value--info">{avgScore}%</div>
          </div>
        </div>

      </div>

      {/* ROW 2: COMBINED AI CONTROL CARD */}
      <div className="glass-panel screening-workspace">
        
        {/* Step Header: Job Selection */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '18px', borderBottom: '1px solid var(--border-color)', marginBottom: '20px' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="step-icon">
              <Briefcase size={20} />
            </div>
            <div>
              <label className="section-eyebrow">Bước 1 · Chọn vị trí tuyển dụng</label>
              <select
                className="select-field"
                value={selectedJob?.id || ''}
                onChange={(e) => {
                  const j = jobs.find((item) => item.id === e.target.value);
                  if (j) selectJob(j);
                }}
                style={{ fontWeight: 600, fontSize: '0.94rem', minWidth: '280px', marginTop: '5px' }}
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
          
          {/* Section A: Versioned criterion weights */}
          {selectedJob && (
            <CriteriaEditor
              job={selectedJob}
              onWeightsChange={(weights, simulation) => {
                setSliderWeights(weights);
                setIsScoreSimulation(simulation);
              }}
              onPublished={(criteriaSet) => {
                setSelectedJob((current) => ({
                  ...current,
                  version: (current.version || 1) + 1,
                  active_criteria_set_id: criteriaSet.id,
                }));
                setIsScoreSimulation(false);
              }}
            />
          )}

          {/* Section B: Integrated PDF Resume Bulk Uploader */}
          <div style={{ flex: '1' }}>
            <BatchUploader
              jobId={selectedJob?.id}
              criteriaSetId={selectedJob?.active_criteria_set_id}
              onBatchCompleted={() => selectedJob && loadScreenings(selectedJob.id)}
            />
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
              fontWeight: 700,
              borderRadius: '12px',
              boxShadow: '0 7px 18px rgba(17, 155, 115, 0.18)'
            }}
          >
            {screeningLoading ? <RefreshCw size={20} className="spin" /> : <Play size={20} />}
            Bước 3 · Bắt đầu sàng lọc bằng AI
          </button>
        </div>

      </div>

      {/* ROW 3: DYNAMIC CANDIDATE RANKING TABLE & EXPORT PANEL */}
      <div>
        {selectedJob && <ExportFeedbackPanel selectedJobId={selectedJob.id} candidateCount={candidates.length} />}

        {selectedJob && <CandidateGrid jobId={selectedJob.id} refreshToken={candidates} onSelectCandidate={setSelectedCandidate} />}
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
        <CandidateReviewDrawer
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
