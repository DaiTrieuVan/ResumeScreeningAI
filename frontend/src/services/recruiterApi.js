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

  throw new RecruiterApiError(
    problem.message || 'Không thể hoàn tất yêu cầu. Vui lòng thử lại.',
    { status: response.status, code: problem.code, details: problem },
  );
}

export function checkRecruiterWorkspace() {
  return recruiterRequest('/health');
}

export { recruiterRequest };
