/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import CandidateGrid from './CandidateGrid';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({
  queryJobCandidates: vi.fn(),
  saveCandidateView: vi.fn(),
  executeBulkAction: vi.fn(),
  compareJobCandidates: vi.fn(),
}));

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe('CandidateGrid blind review', () => {
  it('announces blind mode and renders only the server-masked identity', async () => {
    api.queryJobCandidates.mockResolvedValue({
      privacy_mode: 'BLIND', total: 1, page_size: 25,
      items: [{ application_id: 'app-1', version: 1, candidate_name: 'Ứng viên A1B2C3D4', candidate_email: null, file_name: 'hoso-app-1.pdf', score: 91, mandatory_gate: 'PASSED', stage: 'SHORTLISTED' }],
    });
    render(<CandidateGrid jobId="job-1" criteriaSetId="criteria-1" onSelectCandidate={vi.fn()} />);

    expect(await screen.findByText(/đánh giá ẩn danh đang bật/i)).toBeInTheDocument();
    expect(screen.getByText('Ứng viên A1B2C3D4')).toBeInTheDocument();
    expect(screen.queryByText(/example\.com/i)).not.toBeInTheDocument();
  });
});
