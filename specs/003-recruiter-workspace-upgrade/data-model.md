# Data Model: Recruiter Screening Workspace Upgrade

## Relationship overview

```text
JobPosting 1 ── * ScreeningCriteriaSet 1 ── * Criterion
      │                    │
      │                    └── * ScreeningEvaluation * ── 1 CandidateApplication
      │                                  │
      └── * UploadBatch ── * UploadItem  ├── * CriterionResult ── * EvidenceSnippet
                                         ├── * CandidateTagAssignment
CandidateProfile 1 ── * CandidateApplication
                                         └── * RecruitmentDecisionEvent

User 1 ── * SavedView
User 1 ── * AuditEvent
```

## Core entities

### JobPosting (extended)

Thêm `active_criteria_set_id`, `version` và vòng đời `DRAFT/ACTIVE/CLOSED/ARCHIVED`. Các cột skill/weight cũ được giữ trong giai đoạn compatibility rồi deprecated sau backfill.

### ScreeningCriteriaSet

| Field | Type | Rules |
|---|---|---|
| id | UUID | primary key |
| job_id | UUID | required, indexed |
| version_number | integer | unique per job |
| name | string | recruiter-facing label |
| status | enum | DRAFT, PUBLISHED, RETIRED |
| scoring_weights | object | tổng đúng 1.0 khi publish |
| created_by, published_by | actor id | auditable |
| created_at, published_at | timestamp | publish time immutable |

Published set là bất biến; chỉnh sửa tạo version mới. Mỗi job chỉ có một active published set.

### Criterion

| Field | Type | Rules |
|---|---|---|
| id, criteria_set_id | UUID | required |
| category | enum | SKILL, EXPERIENCE, EDUCATION, LANGUAGE, LOCATION, OTHER |
| importance | enum | MANDATORY, PREFERRED, BONUS |
| label | string | required |
| operator | enum | CONTAINS_ANY, CONTAINS_ALL, MIN_VALUE, EQUALS, CUSTOM_AI |
| expected_value | JSON | phù hợp operator |
| weight | decimal | >= 0; mandatory có thể chỉ làm gate |
| sort_order | integer | stable UI order |

### UploadBatch

Gồm `job_id`, optional pinned `criteria_set_id`, actor, timestamps, status `CREATED/UPLOADING/PROCESSING/COMPLETED/COMPLETED_WITH_ERRORS/CANCELLED` và các counter queued/processing/success/failed/duplicate/cancelled. Counter là projection và phải nhất quán với items.

### UploadItem

| Field | Type | Rules |
|---|---|---|
| id, batch_id | UUID | required |
| client_file_id | string | ổn định cho retry/idempotency |
| original_file_name, mime_type, byte_size | scalar | validate trước xử lý |
| storage_key | string nullable | không trả trực tiếp cho client |
| file_sha256, content_fingerprint | string nullable | indexed |
| status | enum | QUEUED, VALIDATING, PARSING, NEEDS_OCR, DEDUPE_REVIEW, READY, EVALUATING, COMPLETED, FAILED, CANCELLED |
| error_code, user_message, technical_detail | string nullable | technical detail restricted |
| attempt_count, version | integer | retry/concurrency |
| candidate_application_id | UUID nullable | set sau normalize |

**Transitions**: QUEUED → VALIDATING → PARSING → READY → EVALUATING → COMPLETED. Active step có thể sang FAILED. NEEDS_OCR và DEDUPE_REVIEW là pause có thể phục hồi. Chỉ được CANCEL trước EVALUATING.

### DuplicateMatch

Lưu `upload_item_id`, `matched_profile_id`, `match_type` (`EXACT_FILE/CONTACT/SIMILAR_CONTENT`), confidence và resolution (`NEEDS_REVIEW/KEEP_BOTH/LINK_EXISTING/REPLACE/SKIP`) kèm actor/time.

### CandidateProfile

Person-level record chứa PII chuẩn hóa, current title, latest company, relevant experience months, education/skills và confidence theo từng trường. `UNKNOWN` được giữ là null thay vì số 0. Có `anonymized_at` và optimistic `version`.

### CandidateApplication

Một profile ứng tuyển một job; thay cho liên kết job mơ hồ trên CandidateResume. Chứa source resume hiện tại, stage `RECEIVED/AI_ANALYZED/RECRUITER_REVIEW/SHORTLISTED/HR_INTERVIEW/TECH_INTERVIEW/OFFER/HIRED/REJECTED`, AI recommendation, human decision, reason và version.

### ScreeningEvaluation

| Field | Type | Rules |
|---|---|---|
| id, application_id, criteria_set_id, run_id | UUID | required |
| evaluation_type | enum | OFFICIAL, LEGACY |
| status | enum | QUEUED, RUNNING, COMPLETED, FAILED, SUPERSEDED |
| component_scores, overall_score | JSON + decimal | 0..100 |
| mandatory_gate | enum | PASSED, FAILED, NEEDS_REVIEW |
| model_info | JSON | provider/model/prompt version |
| input_fingerprint | string | resume + criteria snapshot |
| evidence_status | enum | AVAILABLE, PARTIAL, UNAVAILABLE_LEGACY |
| evaluated_at | timestamp | immutable |

Prior runs vẫn được giữ; projection xác định latest official evaluation. ScoreSimulation là record ngắn hạn riêng, luôn gắn nhãn simulation và không tự đổi pipeline.

### CriterionResult và EvidenceSnippet

CriterionResult unique theo evaluation/criterion, chứa `MET/NOT_MET/UNKNOWN/NOT_APPLICABLE`, score, confidence, explanation và manual-review flag.

EvidenceSnippet chứa source resume, page 1-based nếu biết, normalized-text offsets, excerpt ngắn, polarity `SUPPORTS/CONTRADICTS/CONTEXT` và confidence. Không có evidence được biểu diễn bằng mảng rỗng + trạng thái rõ, không tạo văn bản giả.

### RecruitmentDecisionEvent

Append-only event gồm application, event type, from/to stage, reason code, note, actor, time, request ID và before/after version. Sửa ghi chú tạo event mới thay vì ghi đè lịch sử.

### CandidateTag / Assignment

Tag organization-scoped, normalized name unique. Assignment unique theo application/tag và có actor/time.

### SavedView

Lưu owner, job, tên view, cấu hình cột, filter expression, sort expression và default flag. Filter dùng schema whitelist có version; không nhận raw SQL.

### BulkActionRequest / BulkActionItem

Request lưu action, selection snapshot/expression, idempotency key, actor và aggregate status. Item lưu application, expected version, result và error. Unique `(actor_id, idempotency_key)` ngăn thực thi lặp.

### AuditEvent

Append-only security/business audit gồm actor, action, resource, timestamp, request ID, metadata đã redacted và outcome. Không lưu raw CV hoặc PII không cần thiết.

## Required indexes

- `(job_id, version_number)` unique và `(job_id, status)` cho criteria.
- `(batch_id, status)`, `file_sha256`, `content_fingerprint` cho upload.
- `(job_id, pipeline_stage, updated_at)`, `(job_id, received_at)` cho application list.
- `(application_id, criteria_set_id, evaluated_at)`, `(criteria_set_id, overall_score)` cho evaluation.
- `(application_id, created_at)` và `(resource_type, resource_id, created_at)` cho history/audit.

## Legacy mapping

- JobPosting skill/experience/education/weights → Criteria version 1.
- CandidateResume → source document + CandidateProfile + CandidateApplication.
- ScreeningResult → legacy ScreeningEvaluation + application projection.
- `recruiter_status` → nearest pipeline stage; feedback note → imported decision note event.
- Legacy evaluation có `evidence_status=UNAVAILABLE_LEGACY`, không được trình bày như evidence-backed.
