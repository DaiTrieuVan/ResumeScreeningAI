import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import CandidateComparison from './CandidateComparison';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({ compareJobCandidates: vi.fn() }));
afterEach(() => cleanup());

describe('CandidateComparison', () => {
  it('renders unknown as missing data instead of failure', async () => {
    api.compareJobCandidates.mockResolvedValue({ criteria_version: 2, candidates: [{ application_id: 'a', candidate_name: 'An', overall_score: 70, pipeline_stage: 'SHORTLISTED', mandatory_gate: 'NEEDS_REVIEW' }], criteria: [{ criterion_id: 'c', label: 'Kubernetes', importance: 'PREFERRED', results: { a: { result: 'UNKNOWN', explanation: 'Không có bằng chứng', evidence: [] } } }] });
    render(<CandidateComparison jobId="j" applicationIds={['a', 'b']} criteriaSetId="v2" onClose={vi.fn()} />);
    expect(await screen.findByText('Chưa đủ dữ liệu')).toBeInTheDocument();
    expect(screen.queryByText('Chưa đạt')).not.toBeInTheDocument();
  });
});
