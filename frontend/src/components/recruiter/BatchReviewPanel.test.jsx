/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import React from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import BatchReviewPanel from './BatchReviewPanel';
import * as api from '../../services/recruiterApi';

vi.mock('../../services/recruiterApi', () => ({ retryUploadBatch: vi.fn(), resolveUploadDuplicate: vi.fn(), recoverUploadBatch: vi.fn(), submitManualRecovery: vi.fn() }));

afterEach(() => cleanup());

describe('BatchReviewPanel', () => {
  it('shows independent success, duplicate and failure outcomes', () => {
    render(<BatchReviewPanel batch={{
      id: 'batch-1', total_count: 3, success_count: 1, failed_count: 1,
      duplicate_count: 1, cancelled_count: 0,
      items: [
        { id: '1', original_file_name: 'ok.pdf', status: 'COMPLETED' },
        { id: '2', original_file_name: 'same.pdf', status: 'DEDUPE_REVIEW', user_message: 'Có thể trùng' },
        { id: '3', original_file_name: 'scan.pdf', status: 'NEEDS_OCR', user_message: 'Cần OCR' },
      ],
    }} />);
    expect(screen.getByText('3/3 hồ sơ đã xử lý')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /thử lại 1 mục lỗi/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /dùng hồ sơ cũ/i })).toBeInTheDocument();
  });

  it('offers a verified-text recovery path for scan-only PDFs', async () => {
    api.submitManualRecovery.mockResolvedValue({ id: 'batch-1', items: [] });
    render(<BatchReviewPanel onUpdated={vi.fn()} batch={{
      id: 'batch-1', status: 'COMPLETED_WITH_ERRORS', total_count: 1, success_count: 0, failed_count: 1, duplicate_count: 0, cancelled_count: 0,
      items: [{ id: 'scan', original_file_name: 'scan.pdf', status: 'NEEDS_OCR', user_message: 'PDF không có lớp chữ' }],
    }} />);
    fireEvent.click(screen.getByText('Nhập nội dung đã xác minh'));
    fireEvent.change(screen.getByLabelText('Văn bản xác minh cho scan.pdf'), { target: { value: 'Python FastAPI experience verified on page one.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Xác nhận và xử lý lại' }));
    expect(api.submitManualRecovery).toHaveBeenCalledWith('scan', 'Python FastAPI experience verified on page one.', 'Đã đối chiếu bản scan');
  });
});
