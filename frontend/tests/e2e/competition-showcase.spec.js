/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import { expect, test } from '@playwright/test';

const json = (body, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) });

test('offline showcase covers recruiter, real-job matching and career-gap guidance', async ({ page }) => {
  const job = { id: 'job-offline', title: 'Backend Engineer', department: 'Engineering', version: 1, active_criteria_set_id: 'criteria-offline', required_skills: ['Python'] };
  const realJob = { id: 'real-1', title: 'Python Engineer', company_name: 'Open Source Lab', location: 'Hà Nội', location_tag: 'HANOI', required_skills: ['Python', 'FastAPI'], description_text: 'Build APIs', source_url: 'https://example.test/job' };

  await page.route('**/api/**', async (route) => {
    const url = route.request().url();
    if (url.endsWith('/api/runtime-status')) return route.fulfill(json({ mode: 'offline', fallback: true, engine: 'deterministic-keyword-v1', external_services: false }));
    if (url.endsWith('/api/real-jobs') && route.request().method() === 'GET') return route.fulfill(json([realJob]));
    if (url.endsWith('/api/real-jobs/match')) return route.fulfill(json([{ real_job: realJob, match_score: 92, skills_sub_score: 95, experience_sub_score: 88, strengths_summary: ['Python'], gaps_summary: ['Cloud'], match_reasoning: 'Deterministic offline match', cv_domain: 'Backend Engineering' }]));
    if (url.endsWith('/api/jobs')) return route.fulfill(json([job]));
    if (url.includes('/screenings/job-offline')) return route.fulfill(json([]));
    if (url.includes('/criteria-sets')) return route.fulfill(json([{ id: 'criteria-offline', version_number: 1, status: 'PUBLISHED', scoring_weights: { skills: 1 }, criteria: [] }]));
    if (url.includes('/review-privacy')) return route.fulfill(json({ job_id: job.id, mode: 'IDENTIFIED', reveal_stage: null, masked_fields: [], version: 1 }));
    if (url.includes('/analytics')) return route.fulfill(json({ funnel: {}, upload_counts: { total: 0, success: 0, failed: 0, duplicate: 0 }, median_processing_seconds: 0, ai_override_rate: 0 }));
    if (url.includes('/candidates?')) return route.fulfill(json({ items: [], total: 0, page: 1, page_size: 25, facets: {}, privacy_mode: 'IDENTIFIED' }));
    if (url.endsWith('/api/gap-advisor/analyze')) return route.fulfill(json({ id: 'gap-1', target_job_title: 'Backend Engineer', matched_skills: ['Python'], missing_skills: ['Docker'], suggested_action_items: ['Hoàn thành một dự án Docker có kiểm thử'], summary_explanation: 'Pipeline deterministic offline đã so sánh CV với JD.', created_at: new Date().toISOString() }));
    return route.fulfill(json({}));
  });

  await page.goto('/');
  await expect(page.getByText(/Offline · deterministic-keyword-v1/i)).toBeVisible();

  await expect(page.getByRole('heading', { name: /Tìm công việc phù hợp/i })).toBeVisible();
  await page.locator('#cv-upload-realjobs').setInputFiles({ name: 'synthetic-cv.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF synthetic') });
  await page.getByRole('button', { name: /Gợi ý việc phù hợp/i }).click();
  await expect(page.getByText(/AI nhận diện chuyên môn:.*Backend Engineering/i)).toBeVisible();
  await expect(page.getByText('92%')).toBeVisible();

  await page.getByRole('button', { name: 'Không gian tuyển dụng' }).click();
  await expect(page.getByRole('heading', { name: 'Tổng quan tuyển dụng' })).toBeVisible();
  await expect(page.locator('.select-field')).toHaveValue('job-offline');

  await page.getByRole('button', { name: 'Cố vấn nghề nghiệp' }).click();
  await page.getByPlaceholder(/Kỹ sư hệ thống AI/i).fill('Backend Engineer');
  await page.getByPlaceholder(/Dán nội dung mô tả công việc/i).fill('Python FastAPI Docker');
  await page.getByRole('button', { name: /Xây dựng lộ trình/i }).click();
  await expect(page.getByText('Docker', { exact: true })).toBeVisible();
  await expect(page.getByText(/Pipeline deterministic offline/i)).toBeVisible();
});
