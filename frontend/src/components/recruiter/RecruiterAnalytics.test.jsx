/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RecruiterAnalytics from './RecruiterAnalytics';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({ fetchRecruiterAnalytics: vi.fn() }));
afterEach(() => cleanup());

describe('RecruiterAnalytics', () => {
  it('shows funnel and operational quality from server aggregates', async () => {
    api.fetchRecruiterAnalytics.mockResolvedValue({ funnel: { SHORTLISTED: 12, REJECTED: 3 }, upload_counts: { success: 90, total: 100, failed: 5, duplicate: 5 }, median_processing_seconds: 42, ai_override_rate: .16 });
    render(<RecruiterAnalytics jobId="job-1" />);
    expect(await screen.findByText('12')).toBeInTheDocument();
    expect(screen.getByText('90/100')).toBeInTheDocument();
    expect(screen.getByText('16%')).toBeInTheDocument();
  });
});
