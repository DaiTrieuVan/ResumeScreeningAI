# Tasks: Final Competition Release

**Input**: Design documents from `specs/004-final-competition-release/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/final-release-api.yaml`, `quickstart.md`

**Tests**: Regression, contract, integration, frontend component, and E2E tests are required by FR-025 and SC-010.

**Organization**: Tasks are grouped by user story so every increment remains independently demonstrable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish final-release directories, configuration, and reproducible fixtures.

- [X] T001 Create evaluation dataset, report, and release artifact directory structure with tracked placeholders in `evaluation/`, `artifacts/benchmark/`, and `release/`
- [X] T002 [P] Add final-release limits, lease duration, retry count, privacy defaults, and artifact paths in `backend/app/core/config.py`
- [X] T003 [P] Add synthetic-only evaluation fixture policy and schema documentation in `evaluation/README.md`
- [X] T004 Verify generated, secret, PII, database, and release-artifact exclusions in `./.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add persistence and shared safety primitives used across all final-release stories.

**CRITICAL**: Complete this phase before any user-story implementation.

- [X] T005 Add failing migration coverage for final-release entities and columns in `backend/tests/integration/test_final_release_migrations.py`
- [X] T006 Define `ResumePage`, `CandidateCorrection`, `ProcessingLease`, `IdempotencyRecord`, `ReviewPrivacyPolicy`, `EvaluationRun`, and `MetricResult` models in `backend/app/models/final_release.py`
- [X] T007 Register final-release models and additive migrations in `backend/app/core/database.py` and `backend/app/core/migrations.py`
- [X] T008 [P] Define shared final-release API schemas and validation in `backend/app/schemas/final_release.py`
- [X] T009 Add persisted request fingerprinting and replay protection in `backend/app/services/idempotency_service.py`
- [X] T010 Add structured audit metadata redaction helpers in `backend/app/services/audit_service.py`
- [X] T011 Run migration tests and mark the foundation complete in `specs/004-final-competition-release/tasks.md`

**Checkpoint**: Database and shared services can support each story without destructive schema changes.

---

## Phase 3: User Story 1 - Chứng minh chất lượng AI bằng số liệu (Priority: P1) MVP

**Goal**: Produce a reproducible, honest AI benchmark report with release traceability and pass/fail thresholds.

**Independent Test**: Run the locked synthetic dataset and verify all five metrics include numerator, denominator, sample size, threshold, configuration, and release identity.

### Tests for User Story 1

- [ ] T012 [P] [US1] Add metric formula and threshold tests in `backend/tests/unit/test_evaluation_service.py`
- [ ] T013 [P] [US1] Add evaluation API contract tests in `backend/tests/contract/test_evaluation_api.py`
- [ ] T014 [P] [US1] Add dataset validation and minimum-coverage tests in `backend/tests/integration/test_evaluation_dataset.py`

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create versioned manifests, three synthetic JDs, and at least thirty synthetic CV labels in `evaluation/datasets/competition-v1/`
- [ ] T016 [US1] Implement dataset validation and mandatory recall, evidence precision, UNKNOWN accuracy, ranking agreement, and batch completion metrics in `backend/app/services/evaluation_service.py`
- [ ] T017 [US1] Implement JSON and Markdown benchmark report generation in `backend/app/services/evaluation_report_service.py`
- [ ] T018 [US1] Implement evaluation run and result endpoints in `backend/app/api/evaluations.py`
- [ ] T019 [US1] Register evaluation routes in `backend/app/main.py`
- [ ] T020 [US1] Add a reproducible benchmark CLI with release SHA/model/fallback metadata in `scripts/run_ai_benchmark.py`
- [ ] T021 [US1] Run the benchmark and store measured reports in `artifacts/benchmark/competition-v1.json` and `artifacts/benchmark/competition-v1.md`

**Checkpoint**: AI claims are backed by reproducible measured evidence rather than target-only statements.

---

## Phase 4: User Story 2 - Kiểm chứng và sửa kết quả trên CV gốc (Priority: P1)

**Goal**: Navigate evidence to its real PDF page, correct extracted data, audit the correction, and invalidate stale evaluations.

**Independent Test**: Open three citations across a multi-page CV, navigate to each page, correct one extracted field, and verify audit plus stale evaluation state.

### Tests for User Story 2

- [ ] T022 [P] [US2] Add page extraction, duplicate excerpt, and unknown-location tests in `backend/tests/unit/test_page_aware_evidence.py`
- [ ] T023 [P] [US2] Add correction concurrency, validation, audit, and stale-state tests in `backend/tests/contract/test_candidate_corrections_api.py`
- [ ] T024 [P] [US2] Add evidence navigation and correction form component tests in `frontend/src/components/recruiter/CandidateReviewDrawer.test.jsx`

### Implementation for User Story 2

- [ ] T025 [US2] Persist per-page text, offsets, and extraction metadata during parsing in `backend/app/services/pdf_parser.py`
- [ ] T026 [US2] Resolve evidence to reliable page locations without fabricating unknown pages in `backend/app/services/evidence_service.py`
- [ ] T027 [US2] Implement authorized field and evidence corrections with optimistic concurrency in `backend/app/services/correction_service.py`
- [ ] T028 [US2] Implement correction endpoint and evidence-location response projection in `backend/app/api/candidates.py`
- [ ] T029 [US2] Expose correction and page-aware evidence operations in `frontend/src/services/recruiterApi.js`
- [ ] T030 [US2] Add clickable evidence, PDF page navigation, unknown-page fallback, and correction UI in `frontend/src/components/recruiter/CandidateReviewDrawer.jsx`
- [ ] T031 [US2] Add stale-evaluation messaging and rerun affordance in `frontend/src/pages/RecruiterDashboard.jsx`
- [ ] T032 [US2] Add page navigation and correction journey coverage in `frontend/tests/e2e/recruiter-workspace.spec.js`

**Checkpoint**: Every displayed evidence location is verifiable or explicitly unknown, and human corrections are traceable.

---

## Phase 5: User Story 3 - Phục hồi CV khó đọc và batch bị gián đoạn (Priority: P1)

**Goal**: Recover unreadable PDFs and interrupted batches safely without duplicate business effects.

**Independent Test**: Process a mixed batch, interrupt it, restart, replay retry/recovery ten times, and verify one outcome per item with an actionable terminal state.

### Tests for User Story 3

- [ ] T033 [P] [US3] Add idempotency replay and payload-conflict tests in `backend/tests/unit/test_idempotency_service.py`
- [ ] T034 [P] [US3] Add lease expiry, retry ceiling, and restart reconciliation tests in `backend/tests/unit/test_upload_recovery_service.py`
- [ ] T035 [P] [US3] Add manual verified-text recovery contract tests in `backend/tests/contract/test_upload_recovery_api.py`
- [ ] T036 [P] [US3] Add recovery controls and failure guidance tests in `frontend/src/components/recruiter/BatchReviewPanel.test.jsx`

### Implementation for User Story 3

- [ ] T037 [US3] Integrate durable idempotency for create, retry, and recover operations in `backend/app/services/upload_batch_service.py`
- [ ] T038 [US3] Implement processing leases, bounded attempts, expired-lease reconciliation, and safe resume in `backend/app/services/upload_recovery_service.py`
- [ ] T039 [US3] Implement manual verified-text recovery and provenance tracking in `backend/app/services/upload_batch_service.py`
- [ ] T040 [US3] Add create idempotency, batch recovery, and manual recovery endpoints in `backend/app/api/upload_batches.py`
- [ ] T041 [US3] Reconcile interrupted work during application startup in `backend/app/main.py`
- [ ] T042 [US3] Add recovery and manual-text API clients in `frontend/src/services/recruiterApi.js`
- [ ] T043 [US3] Add scan guidance, manual recovery form, retry ceiling, and resume controls in `frontend/src/components/recruiter/BatchReviewPanel.jsx`
- [ ] T044 [US3] Add crash/replay/manual-recovery E2E coverage in `frontend/tests/e2e/recruiter-workspace.spec.js`

**Checkpoint**: Mixed batches degrade gracefully and can be resumed without re-uploading successful files.

---

## Phase 6: User Story 4 - Sàng lọc giảm thiên lệch và bảo vệ dữ liệu demo (Priority: P2)

**Goal**: Enforce server-side blind review consistently and audit authorized PII reveal/anonymization.

**Independent Test**: Enable blind review and verify list, detail, compare, evidence, filename, and export contain no configured identifiers; reveal with permission and verify a redacted audit event.

### Tests for User Story 4

- [ ] T045 [P] [US4] Add privacy-policy and reveal authorization contract tests in `backend/tests/contract/test_review_privacy_api.py`
- [ ] T046 [P] [US4] Add server-side list/detail/compare/export/evidence masking tests in `backend/tests/integration/test_blind_review_projections.py`
- [ ] T047 [P] [US4] Add blind-review toggle and masked presentation tests in `frontend/src/components/recruiter/CandidateGrid.test.jsx` and `frontend/src/components/recruiter/CandidateReviewDrawer.test.jsx`

### Implementation for User Story 4

- [ ] T048 [US4] Implement versioned job privacy policy and authorized reveal auditing in `backend/app/services/candidate_privacy_service.py`
- [ ] T049 [US4] Apply blind projections to candidate list, detail, compare, evidence, filename, and export in `backend/app/repositories/candidate_query_repository.py`, `backend/app/services/comparison_service.py`, and `backend/app/api/exports.py`
- [ ] T050 [US4] Add privacy policy and reveal endpoints in `backend/app/api/recruiter.py`
- [ ] T051 [US4] Add review privacy API clients in `frontend/src/services/recruiterApi.js`
- [ ] T052 [US4] Add blind-review controls, explanatory copy, and masked render paths in `frontend/src/pages/RecruiterDashboard.jsx`, `frontend/src/components/recruiter/CandidateGrid.jsx`, and `frontend/src/components/recruiter/CandidateReviewDrawer.jsx`
- [ ] T053 [US4] Add blind-review journey coverage in `frontend/tests/e2e/recruiter-workspace.spec.js`

**Checkpoint**: Initial review can be completed without exposing direct identifiers, while authorized reveal remains accountable.

---

## Phase 7: User Story 5 - Phát hành và trình diễn bản dự thi có thể tái tạo (Priority: P1)

**Goal**: Validate the whole product from clean source in online and offline modes and assemble auditable competition evidence.

**Independent Test**: Clone/copy the intended release source into a clean path, configure from samples, run every gate, complete the full product demo offline, and verify public release evidence.

### Tests for User Story 5

- [ ] T054 [P] [US5] Add secret, PII, tracked-artifact, and synthetic-dataset safety scan tests in `scripts/check_release_safety.ps1`
- [ ] T055 [P] [US5] Add full recruiter, real-jobs, and career-gap offline journey coverage in `frontend/tests/e2e/competition-showcase.spec.js`

### Implementation for User Story 5

- [ ] T056 [US5] Add deterministic offline mode and visible model/fallback status across backend and frontend in `backend/app/core/config.py`, `backend/app/services/embedding_service.py`, and `frontend/src/components/Navbar.jsx`
- [ ] T057 [US5] Add a clean-room build/test/demo validator in `scripts/verify_clean_room.ps1`
- [ ] T058 [US5] Integrate backend, frontend, E2E, compliance, benchmark, and release-safety gates in `.github/workflows/ci.yml`
- [ ] T059 [P] [US5] Document benchmark reproduction and interpretation in `docs/AI_EVALUATION.md`
- [ ] T060 [P] [US5] Document release manifest, checksum, SBOM/license inventory, offline fallback, and known limitations in `docs/RELEASE_GUIDE.md`
- [ ] T061 [P] [US5] Align showcase timing, judge objections, and fallback cues with implemented behavior in `docs/SHOWCASE_SCRIPT.md`
- [ ] T062 [US5] Execute the clean-room and offline showcase gates and record results in `release/verification-record.md`

**Checkpoint**: The intended release is reproducible, inspectable, and demonstrable without external services.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Close documentation, accessibility, performance, and release-gate gaps without expanding product scope.

- [ ] T063 [P] Add regression references and final evidence links to `docs/COMPETITION_CHECKLIST.md`
- [ ] T064 [P] Update architecture, privacy, testing, and deployment documentation in `docs/ARCHITECTURE.md`, `docs/PRIVACY_AND_RESPONSIBLE_AI.md`, `docs/TESTING.md`, and `docs/BUILD_AND_DEPLOYMENT.md`
- [ ] T065 Add accessibility labels, keyboard focus, reduced-motion handling, and responsive validation to final-release UI changes in `frontend/src/styles/index.css`
- [ ] T066 Run all gates defined in `.github/workflows/ci.yml` and fix regressions in affected files under `backend/`, `frontend/`, and `scripts/`
- [ ] T067 Record final measured outcomes, limitations, and unresolved production boundaries in `CHANGELOG.md` and `release/verification-record.md`
- [ ] T068 Verify every task and requirement is evidenced and mark completion in `specs/004-final-competition-release/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on Setup and blocks all stories.
- **US1 (Phase 3)**: Depends on Foundational; provides the measurable AI release gate.
- **US2 (Phase 4)**: Depends on Foundational; benchmark fixtures can reuse its page-aware evidence.
- **US3 (Phase 5)**: Depends on Foundational; integrates with upload persistence.
- **US4 (Phase 6)**: Depends on Foundational and must cover projections introduced by US2.
- **US5 (Phase 7)**: Depends on US1-US4 because it validates and packages their combined behavior.
- **Polish (Phase 8)**: Depends on all selected stories.

### User Story Dependencies

- **US1 (P1)**: Independently testable after Foundational.
- **US2 (P1)**: Independently testable after Foundational; its page metadata improves US1 evidence measurement.
- **US3 (P1)**: Independently testable after Foundational.
- **US4 (P2)**: Independently testable after Foundational, but final masking test includes US2 evidence views.
- **US5 (P1)**: Integration/release story; depends on completed product stories.

### Parallel Opportunities

- T002 and T003 can proceed in parallel after T001.
- Test files marked `[P]` can be authored together before each story implementation.
- Dataset authoring T015 can proceed while T016-T020 are implemented after their tests exist.
- Backend and frontend tasks in US2-US4 can proceed in parallel once their API contract is fixed.
- Documentation tasks T059-T061 and T063-T064 are independent after behavior stabilizes.

---

## Parallel Examples

### User Story 1

```text
T012 metric unit tests | T013 API contract tests | T014 dataset validation tests
T015 synthetic dataset authoring (after schema is agreed)
```

### User Story 2

```text
T022 evidence parser tests | T023 correction contract tests | T024 frontend component tests
T025-T028 backend path, then T029-T032 frontend path
```

### User Story 3

```text
T033 idempotency tests | T034 lease/restart tests | T035 recovery API tests | T036 UI tests
```

### User Story 4

```text
T045 policy tests | T046 projection tests | T047 frontend masking tests
```

### User Story 5

```text
T054 release-safety scan | T055 showcase E2E | T059-T061 documentation
```

---

## Implementation Strategy

### Evidence-First MVP

1. Complete Setup and Foundational persistence.
2. Deliver US1 so every AI claim has a measurable baseline.
3. Deliver US2 and rerun US1 to validate page-aware evidence.
4. Stop and demonstrate benchmark plus verifiable correction before adding recovery/privacy.

### Incremental Final Release

1. Foundation -> stable schema, idempotency, and audit primitives.
2. US1 -> measurable AI quality.
3. US2 -> evidence-first human review.
4. US3 -> failure-tolerant bulk processing.
5. US4 -> responsible blind review.
6. US5 -> clean-room, offline, and public-release evidence.
7. Polish -> full gate and honest limitation record.

## Notes

- `[P]` means different files or no dependency on an incomplete task.
- Every user-story task contains its traceability label and exact target path.
- Tests are written before their corresponding implementation and retained as release gates.
- Commit logical, tested slices; do not merge, tag, push, or publish until the release gate is reviewed.
- Do not add email, scheduling, chatbot, ATS integration, or multi-node infrastructure to this feature.
