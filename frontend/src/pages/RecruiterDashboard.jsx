import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Play, RefreshCw, Sliders } from 'lucide-react';
import { fetchJobs, triggerScreening, fetchJobScreenings } from '../services/api';
import JobPostingForm from '../components/JobPostingForm';
import ResumeUploader from '../components/ResumeUploader';
import CandidateTable from '../components/CandidateTable';
import CandidateDetailModal from '../components/CandidateDetailModal';
import ExportFeedbackPanel from '../components/ExportFeedbackPanel';

export default function RecruiterDashboard() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  
  const [showJobForm, setShowJobForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [screeningLoading, setScreeningLoading] = useState(false);

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
    setSliderWeights({
      wSkills: job.weight_skills,
      wExp: job.weight_experience,
      wEdu: job.weight_education
    });
    loadScreenings(job.id);
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
    try {
      const results = await triggerScreening(selectedJob.id);
      setCandidates(results);
    } catch (err) {
      alert('Lỗi sàng lọc AI: ' + err.message);
    } finally {
      setScreeningLoading(false);
    }
  };

  const handleJobCreated = (newJob) => {
    setJobs((prev) => [newJob, ...prev]);
    setShowJobForm(false);
    selectJob(newJob);
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
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => setShowJobForm(true)} className="btn btn-secondary">
            <Plus size={16} /> Tạo Yêu cầu Mới
          </button>

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
      <ResumeUploader onResumesUploaded={() => selectedJob && loadScreenings(selectedJob.id)} />

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
          onJobCreated={handleJobCreated}
          onClose={() => setShowJobForm(false)}
        />
      )}

      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}

    </div>
  );
}
