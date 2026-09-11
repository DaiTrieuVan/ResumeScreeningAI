import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { StaleResultNotice, WorkspaceError, WorkspaceLoading } from './WorkspaceStates';


describe('workspace states', () => {
  it('announces loading state', () => {
    render(<WorkspaceLoading label="Đang chuẩn bị hồ sơ" />);
    expect(screen.getByRole('status')).toHaveTextContent('Đang chuẩn bị hồ sơ');
  });

  it('lets recruiter retry an error', () => {
    const retry = vi.fn();
    render(<WorkspaceError message="Tải thất bại" onRetry={retry} />);
    fireEvent.click(screen.getByRole('button', { name: /thử lại/i }));
    expect(retry).toHaveBeenCalledOnce();
  });

  it('does not imply a stale score was recomputed', () => {
    render(<StaleResultNotice />);
    expect(screen.getByText(/điểm chính thức không đổi/i)).toBeInTheDocument();
  });
});
