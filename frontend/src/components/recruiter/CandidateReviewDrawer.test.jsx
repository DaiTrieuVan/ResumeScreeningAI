import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import CandidateReviewDrawer from './CandidateReviewDrawer';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({
  fetchCandidateDetail: vi.fn(),
  getOriginalResumeUrl: vi.fn(() => '/resume.pdf'),
}));

describe('CandidateReviewDrawer', () => {
  it('shows source evidence and keeps unknown distinct from failure', async () => {
    api.fetchCandidateDetail.mockResolvedValue({
      application_id: 'app-1', candidate_name: 'Nguyễn Minh', candidate_email: 'minh@example.com',
      evaluation: {
        overall_score: 82, mandatory_gate: 'PASS', evidence_status: 'PARTIAL',
        criterion_results: [
          { id: 'r1', label: 'Python', importance: 'MUST_HAVE', result: 'MET', explanation: 'Có kỹ năng trực tiếp.', evidence: [{ id: 'e1', excerpt: '5 years building Python services', confidence: 0.94 }] },
          { id: 'r2', label: 'Kubernetes', importance: 'MUST_HAVE', result: 'UNKNOWN', explanation: 'Không thấy thông tin.', evidence: [] },
        ],
      },
    });

    render(<CandidateReviewDrawer candidate={{ application_id: 'app-1', candidate_name: 'Nguyễn Minh' }} onClose={vi.fn()} />);

    expect(await screen.findByText(/5 years building Python services/i)).toBeInTheDocument();
    expect(screen.getByText('Chưa đủ dữ liệu')).toBeInTheDocument();
    expect(screen.getByText(/không tìm thấy bằng chứng trực tiếp/i)).toBeInTheDocument();
    expect(screen.queryByText('Chưa đạt')).not.toBeInTheDocument();
  });
});
