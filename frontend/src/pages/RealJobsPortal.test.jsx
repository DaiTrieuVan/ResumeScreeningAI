/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

import RealJobsPortal from './RealJobsPortal';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('keeps the jobs portal usable when the jobs endpoint returns a non-array payload', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ detail: 'temporary fallback response' }),
  });
  vi.stubGlobal('fetch', fetchMock);

  render(<RealJobsPortal />);

  expect(screen.getByRole('heading', { name: /tìm công việc phù hợp/i })).toBeInTheDocument();
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/real-jobs'));
  expect(screen.queryAllByRole('article')).toHaveLength(0);
});
