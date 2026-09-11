const RECRUITER_API_BASE = '/api/recruiter';

export class RecruiterApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = 'RecruiterApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function createIdempotencyKey(prefix = 'recruiter') {
  const randomId = globalThis.crypto?.randomUUID?.()
    || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${prefix}-${randomId}`;
}

async function recruiterRequest(path, options = {}) {
  const response = await fetch(`${RECRUITER_API_BASE}${path}`, options);
  if (response.ok) {
    if (response.status === 204) return null;
    return response.json();
  }

  let problem = {};
  try {
    problem = await response.json();
  } catch {
    problem = {};
  }

  const details = problem.detail || problem;
  throw new RecruiterApiError(
    details.message || 'Không thể hoàn tất yêu cầu. Vui lòng thử lại.',
    { status: response.status, code: details.code, details },
  );
}

export function checkRecruiterWorkspace() {
  return recruiterRequest('/health');
}

export function fetchCriteriaSets(jobId) {
  return recruiterRequest(`/jobs/${jobId}/criteria-sets`);
}

export function createCriteriaSet(jobId, payload) {
  return recruiterRequest(`/jobs/${jobId}/criteria-sets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function publishCriteriaSet(criteriaSetId, jobVersion) {
  return recruiterRequest(`/criteria-sets/${criteriaSetId}/publish`, {
    method: 'POST',
    headers: { 'If-Match': String(jobVersion) },
  });
}

export function simulateScore(componentScores, proposedWeights) {
  return recruiterRequest('/score-simulations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ component_scores: componentScores, proposed_weights: proposedWeights }),
  });
}

export function createUploadBatch(jobId, files, criteriaSetId = null) {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  if (criteriaSetId) formData.append('criteria_set_id', criteriaSetId);
  return recruiterRequest(`/jobs/${jobId}/upload-batches`, {
    method: 'POST',
    body: formData,
  });
}

export function fetchUploadBatch(batchId) {
  return recruiterRequest(`/upload-batches/${batchId}`);
}

export function retryUploadBatch(batchId, itemIds = []) {
  return recruiterRequest(`/upload-batches/${batchId}/retry`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': createIdempotencyKey('retry'),
    },
    body: JSON.stringify({
      scope: itemIds.length ? 'SELECTED' : 'FAILED_ONLY',
      item_ids: itemIds,
    }),
  });
}

export function resolveUploadDuplicate(itemId, resolution) {
  return recruiterRequest(`/upload-items/${itemId}/duplicate-resolution`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolution }),
  });
}

export function fetchCandidateDetail(applicationId) {
  return recruiterRequest(`/applications/${applicationId}`);
}

export function getOriginalResumeUrl(applicationId) {
  return `${RECRUITER_API_BASE}/applications/${applicationId}/resume`;
}

export function queryJobCandidates(jobId, params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) value.forEach((item) => query.append(key, item));
    else if (value !== '' && value !== null && value !== undefined) query.set(key, value);
  });
  return recruiterRequest(`/jobs/${jobId}/candidates?${query}`);
}

export function saveCandidateView(jobId, payload) {
  return recruiterRequest(`/jobs/${jobId}/saved-views`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  });
}

export function executeBulkAction(jobId, payload) {
  return recruiterRequest(`/jobs/${jobId}/bulk-actions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': createIdempotencyKey('bulk') }, body: JSON.stringify(payload),
  });
}

export function fetchDecisionTimeline(applicationId) {
  return recruiterRequest(`/applications/${applicationId}/decisions`);
}

export function appendCandidateDecision(applicationId, version, payload) {
  return recruiterRequest(`/applications/${applicationId}/decisions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'If-Match': String(version) },
    body: JSON.stringify(payload),
  });
}

export function compareJobCandidates(jobId, applicationIds, criteriaSetId) {
  return recruiterRequest(`/jobs/${jobId}/comparisons`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ application_ids: applicationIds, criteria_set_id: criteriaSetId }),
  });
}

export { recruiterRequest };
