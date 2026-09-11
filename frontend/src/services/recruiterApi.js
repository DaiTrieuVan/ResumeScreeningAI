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

export { recruiterRequest };
