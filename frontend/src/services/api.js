const API_BASE = '/api';

export async function fetchJobs() {
  const res = await fetch(`${API_BASE}/jobs`);
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function createJob(jobData) {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jobData),
  });
  if (!res.ok) throw new Error('Failed to create job posting');
  return res.json();
}

export async function uploadResumes(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload resumes');
  return res.json();
}

export async function triggerScreening(jobId, resumeIds = null) {
  const res = await fetch(`${API_BASE}/screenings/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, resume_ids: resumeIds }),
  });
  if (!res.ok) throw new Error('Failed to run screening evaluation');
  return res.json();
}

export async function fetchJobScreenings(jobId) {
  const res = await fetch(`${API_BASE}/screenings/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch screening results');
  return res.json();
}

export async function updateCandidateStatus(screeningId, status, notes = null, scoreOverride = null) {
  const res = await fetch(`${API_BASE}/screenings/${screeningId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      recruiter_status: status,
      recruiter_feedback_notes: notes,
      score_override: scoreOverride,
    }),
  });
  if (!res.ok) throw new Error('Failed to update status');
  return res.json();
}

export async function analyzeGap(jobTitle, jobDescription, cvFile = null) {
  const formData = new FormData();
  if (jobTitle) formData.append('job_title', jobTitle);
  formData.append('job_description', jobDescription);
  if (cvFile) formData.append('file', cvFile);

  const res = await fetch(`${API_BASE}/gap-advisor/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to generate career gap analysis');
  return res.json();
}

export function getExportCsvUrl(jobId, statusFilter = 'SHORTLISTED') {
  return `${API_BASE}/exports/csv/${jobId}?status_filter=${statusFilter}`;
}
