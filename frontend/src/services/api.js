/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

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

export async function updateJob(jobId, jobData) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jobData),
  });
  if (!res.ok) throw new Error('Failed to update job posting');
  return res.json();
}

export async function deleteJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete job posting');
  return true;
}

export async function uploadResumes(files, jobId = null) {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  if (jobId) formData.append('job_id', jobId);
  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload resumes');
  return res.json();
}

export async function uploadSingleResume(file, jobId = null) {
  const formData = new FormData();
  formData.append('files', file);
  if (jobId) formData.append('job_id', jobId);
  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Failed to upload file ${file.name}`);
  const data = await res.json();
  return data[0];
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

export async function triggerScreeningStream(jobId, resumeIds = null, onProgress = null) {
  const res = await fetch(`${API_BASE}/screenings/evaluate/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, resume_ids: resumeIds }),
  });

  if (!res.ok) throw new Error('Failed to start AI evaluation stream');

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';
  let finalResults = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const payload = JSON.parse(line.slice(6));
          if (onProgress) onProgress(payload);
          if (payload.stage === 'completed') {
            finalResults = payload.results || [];
          } else if (payload.stage === 'error') {
            throw new Error(payload.message || 'Error occurred during AI processing');
          }
        } catch (e) {
          if (e.message && e.message.includes('Error occurred')) throw e;
          console.warn('Failed to parse SSE event:', e, line);
        }
      }
    }
  }

  return finalResults;
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
