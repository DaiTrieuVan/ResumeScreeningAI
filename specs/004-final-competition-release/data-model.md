# Data Model: Final Competition Release

## Quan hệ tổng quát

```text
EvaluationDataset 1 ── * EvaluationRun 1 ── * MetricResult

CandidateResume 1 ── * ResumePage
CandidateResume 1 ── * CandidateCorrection
ResumePage 1 ── * EvidenceSnippet

UploadItem 1 ── 0..1 ProcessingLease
Actor + IdempotencyKey 1 ── 1 IdempotencyRecord

JobPosting 1 ── 1 ReviewPrivacyPolicy
ReleaseEvidence ── references EvaluationRun + immutable commit/tag
```

## EvaluationDataset

| Field | Type | Rules |
|---|---|---|
| id | string | Stable ID |
| version | string | Required, immutable after publish |
| title | string | Required |
| description | text | Scope and limitations |
| license | string | Required |
| provenance | text | Synthetic/anonymous source statement |
| manifest_sha256 | string | Required |
| sample_count | integer | At least 30 for final gate |
| job_count | integer | At least 3 for final gate |
| label_schema_version | string | Required |
| status | enum | DRAFT, REVIEWED, PUBLISHED |

Dataset manifest references JD, CV text/PDF fixtures, criterion labels, expected outcomes/evidence and expert ranking. PUBLISHED datasets are immutable; fixes create a new version.

## EvaluationRun

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| dataset_id/version | reference | Required |
| release_version | string | Required for final report |
| commit_sha | string | Required |
| criteria_versions | JSON | Required |
| model_provider/name/version | strings | Explicit fallback values allowed |
| prompt_version | string | Required if LLM enabled |
| fallback_mode | boolean | Required |
| status | enum | QUEUED, RUNNING, PASSED, FAILED, ERROR |
| started_at/completed_at | datetime | UTC-aware |
| report_json_path/report_md_path | strings | Generated artifacts, not PII |

State transition: `QUEUED -> RUNNING -> PASSED|FAILED|ERROR`. PASSED means all release thresholds met; ERROR means metric could not be computed.

## MetricResult

| Field | Type | Rules |
|---|---|---|
| evaluation_run_id | reference | Required |
| metric_name | enum | MANDATORY_RECALL, EVIDENCE_PRECISION, UNKNOWN_ACCURACY, RANKING_AGREEMENT, BATCH_COMPLETION |
| numerator | number | Required where applicable |
| denominator | number | Greater than zero where applicable |
| value | number | Derived, not hand-entered |
| threshold | number | Versioned release threshold |
| status | enum | PASSED, FAILED, NOT_COMPUTABLE |
| notes | text | No PII |

Unique key: `(evaluation_run_id, metric_name)`.

## ResumePage

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| resume_id | reference | Cascade delete |
| page_number | integer | 1-based, unique per resume |
| text | text | Sensitive; follows resume retention |
| normalized_start_offset | integer | Inclusive |
| normalized_end_offset | integer | Exclusive, >= start |
| extraction_method | enum | NATIVE, OCR, MANUAL |
| confidence | decimal | 0..1 or null for native/manual verified |
| checksum | string | Detect changed extraction |

## EvidenceSnippet additions

- `resume_page_id`: nullable reference for legacy evidence.
- `page_number`: preserved for response stability and validated against ResumePage.
- `bbox_json`: optional `{x0, top, x1, bottom}` when source coordinates are reliable.
- `source_method`: NATIVE, OCR, MANUAL, LEGACY_UNKNOWN.
- `verified_by`, `verified_at`: nullable human verification metadata.

Invariant: evidence may have unknown source location, but MUST NOT contain a fabricated page number or coordinates.

## CandidateCorrection

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| resume_id/application_id | references | Required |
| field_path | string | Allowlisted paths only |
| old_value_redacted | JSON | PII-safe audit representation |
| new_value | JSON | Validated by field schema |
| reason | text | Required |
| actor_id | string | Required |
| source_page_id/evidence_id | references | Optional |
| affects_evaluation | boolean | Required |
| created_at | datetime | Append-only |

Allowed correction areas for final: name/contact, extracted skills, work history, education and manual source text. A correction affecting criteria sets latest evaluation stale; it never mutates an historical evaluation.

## ProcessingLease

| Field | Type | Rules |
|---|---|---|
| upload_item_id | reference | Unique |
| owner_id | string | Worker/process instance |
| lease_token | string | Random, unique |
| acquired_at/expires_at | datetime | UTC-aware |
| heartbeat_at | datetime | Must not exceed expires_at |
| attempt | integer | Positive, bounded |

Claim succeeds only when no lease exists or prior lease expired. Completion checks the lease token to prevent stale worker commit.

## IdempotencyRecord

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| actor_id | string | Required |
| operation | string | CREATE_BATCH, RETRY_BATCH, RECOVER_BATCH, CORRECT_PROFILE |
| idempotency_key | string | Required |
| request_fingerprint | string | Required |
| resource_id | string | Created/affected resource |
| response_status | integer | Required after completion |
| response_body | JSON | PII-minimized |
| status | enum | IN_PROGRESS, COMPLETED, FAILED |
| created_at/expires_at | datetime | Required |

Unique key: `(actor_id, operation, idempotency_key)`. Reuse with a different fingerprint returns conflict; reuse with the same fingerprint returns the stored result.

## ReviewPrivacyPolicy

| Field | Type | Rules |
|---|---|---|
| job_id | reference | Unique |
| mode | enum | IDENTIFIED, BLIND |
| reveal_stage | enum | Optional pipeline stage |
| masked_fields | JSON | Server-controlled allowlist |
| updated_by/updated_at | actor/time | Required |
| version | integer | Optimistic locking |

Blind projection applies to candidate list, detail, comparison, evidence, filenames and exports. Raw storage remains unchanged and protected.

## ReleaseEvidence

Stored as a versioned manifest in the repository/release rather than application business data.

Required fields: semantic version, commit SHA, annotated tag, artifact names, SHA-256 checksums, CI run reference, test counts, benchmark run, dataset version, dependency/license report, clean-room verifier/date/environment and demo asset inventory.

## Migration and compatibility

- Additive migrations only; existing resumes receive page mapping lazily or during explicit backfill.
- Existing evidence remains `LEGACY_UNKNOWN` until regenerated; no fake page assignment.
- Existing batches without leases remain readable; only active/retried items enter lease flow.
- Default privacy mode is IDENTIFIED to preserve current behavior; demo seed explicitly enables BLIND where showcased.
- Rollback keeps new tables/data and disables new behavior via configuration; it does not destructively downgrade records.
