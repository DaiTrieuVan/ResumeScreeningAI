import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import CriteriaEditor from './CriteriaEditor';
import * as api from '../../services/recruiterApi';


vi.mock('../../services/recruiterApi', () => ({
  fetchCriteriaSets: vi.fn(), createCriteriaSet: vi.fn(), publishCriteriaSet: vi.fn(),
}));

const job = {
  id: 'job-1', version: 1, required_skills: ['Python'], min_years_experience: 3,
  weight_skills: 0.5, weight_experience: 0.35, weight_education: 0.15,
};

describe('CriteriaEditor', () => {
  beforeEach(() => {
    api.fetchCriteriaSets.mockResolvedValue([{
      id: 'set-1', version_number: 1, status: 'PUBLISHED',
      scoring_weights: { skills: 0.5, experience: 0.35, education: 0.15 }, criteria: [],
    }]);
  });

  it('labels unsaved weights as a simulation and blocks an invalid total', async () => {
    render(<CriteriaEditor job={job} />);
    await screen.findByText(/phiên bản 1/i);

    const skills = screen.getByLabelText(/kỹ năng chuyên môn/i);
    fireEvent.change(skills, { target: { value: '60' } });

    expect(screen.getByText(/điểm mô phỏng/i)).toBeInTheDocument();
    expect(screen.getByText(/vượt 10%/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /lưu thành phiên bản mới/i })).toBeDisabled();
  });
});
