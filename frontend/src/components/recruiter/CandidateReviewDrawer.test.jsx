/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import CandidateReviewDrawer from './CandidateReviewDrawer';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({
  fetchCandidateDetail: vi.fn(),
  getOriginalResumeUrl: vi.fn(() => '/resume.pdf'),
  fetchDecisionTimeline: vi.fn(() => Promise.resolve([])),
  appendCandidateDecision: vi.fn(),
  correctCandidateData: vi.fn(),
}));

afterEach(() => cleanup());

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

  it('navigates the embedded PDF to a reliable evidence page', async () => {
    api.fetchCandidateDetail.mockResolvedValue({
      application_id: 'app-page', application_version: 1, candidate_name: 'Ứng viên', extracted_skills: [],
      evaluation: { overall_score: 90, mandatory_gate: 'PASSED', evidence_status: 'AVAILABLE', criterion_results: [
        { id: 'r-page', label: 'FastAPI', importance: 'MANDATORY', result: 'MET', explanation: 'Có bằng chứng.', evidence: [
          { id: 'e-page', excerpt: 'Built FastAPI services', page_number: 3, confidence: 0.95 },
        ] },
      ] },
    });
    render(<CandidateReviewDrawer candidate={{ application_id: 'app-page' }} onClose={vi.fn()} />);
    fireEvent.click(await screen.findByRole('button', { name: /Built FastAPI services/i }));
    expect(screen.getByTitle(/CV của/i)).toHaveAttribute('src', '/resume.pdf#page=3');
  });

  it('renders outside transformed page containers and restores page scrolling on close', async () => {
    api.fetchCandidateDetail.mockResolvedValue({
      application_id: 'app-2', candidate_name: 'Trần An', evaluation: null,
    });
    const onClose = vi.fn();
    const { unmount } = render(
      <div className="animate-fade-in"><CandidateReviewDrawer candidate={{ application_id: 'app-2' }} onClose={onClose} /></div>,
    );

    const dialog = await screen.findByRole('dialog');
    expect(dialog.parentElement.parentElement).toBe(document.body);
    expect(document.body.style.overflow).toBe('hidden');
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledOnce();
    unmount();
    expect(document.body.style.overflow).toBe('');
  });
});
