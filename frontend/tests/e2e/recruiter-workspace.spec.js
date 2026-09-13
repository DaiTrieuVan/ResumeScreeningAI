/* SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai */
/* SPDX-License-Identifier: MIT */

import { expect, test } from '@playwright/test';

const json = (body) => ({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });

test.beforeEach(async ({ page }) => {
  const job = { id: 'job-1', title: 'Backend Engineer', department: 'Technology', version: 1, active_criteria_set_id: 'criteria-1', required_skills: ['Python'], weight_skills: .5, weight_experience: .35, weight_education: .15 };
  const criteria = [{ id: 'criteria-1', version_number: 1, status: 'PUBLISHED', scoring_weights: { skills: .5, experience: .35, education: .15 }, criteria: [] }];
  const candidate = { application_id: 'app-1', version: 1, candidate_name: 'Nguyễn An', candidate_email: 'an@example.com', file_name: 'an.pdf', stage: 'AI_ANALYZED', score: 82, mandatory_gate: 'NEEDS_REVIEW', skills: ['Python'] };
  const secondCandidate = { application_id: 'app-2', version: 1, candidate_name: 'Trần Bình', candidate_email: 'binh@example.com', file_name: 'binh.pdf', stage: 'RECRUITER_REVIEW', score: 78, mandatory_gate: 'PASSED', skills: ['Python', 'FastAPI'] };
  await page.route('**/api/**', async (route) => {
    const url = route.request().url();
    if (url.endsWith('/api/jobs')) return route.fulfill(json([job]));
    if (url.includes('/screenings/job-1')) return route.fulfill(json([{ id: 'screen-1', ...candidate, overall_score: 82, recruiter_status: 'NEW' }]));
    if (url.includes('/criteria-sets')) return route.fulfill(json(criteria));
    if (url.includes('/analytics')) return route.fulfill(json({ funnel: { AI_ANALYZED: 1 }, upload_counts: { total: 1, success: 1, failed: 0, duplicate: 0 }, median_processing_seconds: 2, ai_override_rate: 0 }));
    if (url.includes('/candidates?')) return route.fulfill(json({ items: [candidate, secondCandidate], total: 2, page: 1, page_size: 25, facets: {} }));
    if (url.includes('/comparisons')) return route.fulfill(json({ criteria_set_id: 'criteria-1', criteria_version: 1, candidates: [{ ...candidate, overall_score: 82, pipeline_stage: candidate.stage }, { ...secondCandidate, overall_score: 78, pipeline_stage: secondCandidate.stage }], criteria: [{ criterion_id: 'criterion-python', label: 'Python', importance: 'MANDATORY', results: { 'app-1': { result: 'MET', explanation: 'Có bằng chứng Python', evidence: [] }, 'app-2': { result: 'UNKNOWN', explanation: 'Chưa đủ dữ liệu', evidence: [] } } }] }));
    if (url.includes('/upload-items/scan-item/manual-recovery')) return route.fulfill(json({ id: 'batch-scan', status: 'PROCESSING', total_count: 1, success_count: 0, failed_count: 0, duplicate_count: 0, cancelled_count: 0, items: [{ id: 'scan-item', original_file_name: 'scan.pdf', status: 'QUEUED', extraction_method: 'MANUAL' }] }));
    if (url.includes('/jobs/job-1/upload-batches')) return route.fulfill({ status: 202, contentType: 'application/json', body: JSON.stringify({ id: 'batch-scan', status: 'COMPLETED_WITH_ERRORS', total_count: 1, success_count: 0, failed_count: 1, duplicate_count: 0, cancelled_count: 0, items: [{ id: 'scan-item', original_file_name: 'scan.pdf', status: 'NEEDS_OCR', error_code: 'OCR_REQUIRED', user_message: 'PDF không có lớp chữ' }] }) });
    if (url.endsWith('/applications/app-1/corrections')) return route.fulfill(json({ application_id: 'app-1', application_version: 2, evaluation_stale: true }));
    if (url.endsWith('/applications/app-1')) return route.fulfill(json({ application_id: 'app-1', application_version: 1, pipeline_stage: 'AI_ANALYZED', candidate_name: 'Nguyễn An', candidate_email: 'an@example.com', file_name: 'an.pdf', extracted_skills: ['Python'], evaluation: { overall_score: 82, mandatory_gate: 'NEEDS_REVIEW', evidence_status: 'PARTIAL', criterion_results: Array.from({ length: 18 }, (_, index) => ({ id: `result-${index}`, label: `Tiêu chí ${index + 1}`, importance: 'PREFERRED', result: index === 0 ? 'MET' : 'UNKNOWN', confidence: index === 0 ? .95 : .2, explanation: index === 0 ? 'Có bằng chứng trực tiếp.' : 'Chưa có bằng chứng', evidence: index === 0 ? [{ id: 'evidence-page-3', excerpt: 'Built Python APIs', page_number: 3, confidence: .95, source_method: 'NATIVE' }] : [] })) } }));
    if (url.includes('/decisions')) return route.fulfill(json([]));
    if (url.endsWith('/resume')) return route.fulfill({ status: 200, contentType: 'application/pdf', body: '%PDF-1.4' });
    return route.fulfill(json({}));
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Không gian tuyển dụng' }).click();
});

test('keyboard flow keeps controls reachable at desktop and evidence panel scrollable', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'Tổng quan tuyển dụng' })).toBeVisible();
  await expect(page.getByText('Nguyễn An')).toBeVisible();
  await page.getByRole('button', { name: 'Xem' }).first().focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: /Đánh giá hồ sơ/ });
  await expect(dialog).toBeVisible();
  const analysis = dialog.getByRole('region', { name: 'Đánh giá theo tiêu chí' });
  await analysis.evaluate((element) => { element.scrollTop = element.scrollHeight; });
  expect(await analysis.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
});

test('tablet viewport preserves recruiter actions', async ({ page }) => {
  await page.setViewportSize({ width: 900, height: 700 });
  await expect(page.getByRole('button', { name: /Bắt đầu sàng lọc/ })).toBeVisible();
  await expect(page.getByText('Funnel và chất lượng xử lý')).toBeVisible();
});

test('multi-page triage selection opens a same-criteria comparison and preserves unknown', async ({ page }) => {
  const candidateCheckboxes = page.locator('.candidate-grid__table tbody input[type="checkbox"]');
  await candidateCheckboxes.nth(0).check();
  await candidateCheckboxes.nth(1).check();
  await page.getByRole('button', { name: 'So sánh 2–5 hồ sơ' }).click();
  const dialog = page.getByRole('dialog', { name: 'So sánh ứng viên' });
  await expect(dialog).toContainText('cùng phiên bản tiêu chí 1');
  await expect(dialog).toContainText('Nguyễn An');
  await expect(dialog).toContainText('Trần Bình');
  await expect(dialog.getByText('Chưa đủ dữ liệu').first()).toBeVisible();
});

test('evidence opens its PDF page and recruiter can submit an audited correction', async ({ page }) => {
  await page.getByRole('button', { name: 'Xem' }).first().click();
  const dialog = page.getByRole('dialog', { name: /Đánh giá hồ sơ/ });
  await dialog.getByRole('button', { name: /Built Python APIs/i }).click();
  await expect(dialog.getByTitle(/CV của/i)).toHaveAttribute('src', /#page=3$/);

  await dialog.getByText('Hiệu chỉnh dữ liệu AI').click();
  await dialog.getByLabel('Lý do hiệu chỉnh').fill('Đã đối chiếu CV gốc');
  const correctionRequest = page.waitForRequest((request) => request.url().endsWith('/applications/app-1/corrections'));
  await dialog.getByRole('button', { name: 'Lưu và đánh dấu cần chạy lại' }).click();
  const request = await correctionRequest;
  expect(request.headers()['idempotency-key']).toBeTruthy();
  expect(request.postDataJSON().field_path).toBe('extracted_skills');
});

test('scan-only CV has a manual recovery path without re-uploading the batch', async ({ page }) => {
  await page.locator('.batch-dropzone input[type="file"]').setInputFiles({ name: 'scan.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF scan') });
  await page.getByRole('button', { name: 'Tải lên 1 CV' }).click();
  await page.getByText('Nhập nội dung đã xác minh').click();
  await page.getByLabel('Văn bản xác minh cho scan.pdf').fill('Verified Python and FastAPI experience from scan.');
  const requestPromise = page.waitForRequest((request) => request.url().includes('/upload-items/scan-item/manual-recovery'));
  await page.getByRole('button', { name: 'Xác nhận và xử lý lại' }).click();
  const request = await requestPromise;
  expect(request.headers()['idempotency-key']).toBeTruthy();
  expect(request.postDataJSON().mode).toBe('VERIFIED_TEXT');
});
