import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import BatchReviewPanel from './BatchReviewPanel';

vi.mock('../../services/recruiterApi', () => ({ retryUploadBatch: vi.fn(), resolveUploadDuplicate: vi.fn() }));

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
});
