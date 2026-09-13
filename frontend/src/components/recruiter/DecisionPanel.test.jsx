/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import DecisionPanel from './DecisionPanel';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({ fetchDecisionTimeline: vi.fn(), appendCandidateDecision: vi.fn() }));
afterEach(() => cleanup());

describe('DecisionPanel', () => {
  it('requires a rejection reason before calling the API', async () => {
    api.fetchDecisionTimeline.mockResolvedValue([]);
    render(<DecisionPanel applicationId="app-1" version={1} currentStage="AI_ANALYZED" />);
    fireEvent.change(screen.getByLabelText('Giai đoạn'), { target: { value: 'REJECTED' } });
    fireEvent.click(screen.getByRole('button', { name: /cập nhật giai đoạn/i }));
    expect(await screen.findByText(/vui lòng chọn lý do/i)).toBeInTheDocument();
    expect(api.appendCandidateDecision).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText('Lý do từ chối'), { target: { value: 'SKILL_GAP' } });
    api.appendCandidateDecision.mockResolvedValue({ id: 'event-1', event_type: 'HUMAN_DECISION', decision: 'REJECT', to_stage: 'REJECTED', actor_id: 'system', created_at: new Date().toISOString() });
    fireEvent.click(screen.getByRole('button', { name: /cập nhật giai đoạn/i }));
    await waitFor(() => expect(api.appendCandidateDecision).toHaveBeenCalledWith('app-1', 1, expect.objectContaining({ reason_code: 'SKILL_GAP' })));
  });
});
