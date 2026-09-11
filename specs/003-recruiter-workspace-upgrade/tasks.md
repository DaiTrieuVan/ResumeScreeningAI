# Tasks: Recruiter Screening Workspace Upgrade

**Input**: Design documents from `/specs/003-recruiter-workspace-upgrade/`

**Organization**: Tasks are grouped by independently testable recruiter user stories. Tests are included because the feature specification defines measurable acceptance journeys and the plan requires contract/integration gates.

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Verify ignore rules and create feature-oriented backend/frontend recruiter directories in `backend/app/` and `frontend/src/components/recruiter/`
- [X] T002 Add a versioned database migration runner in `backend/app/core/migrations.py` and wire it through `backend/app/core/database.py`
- [X] T003 [P] Add frontend unit-test scripts and dependencies in `frontend/package.json`
- [X] T004 [P] Add backend shared enum definitions in `backend/app/models/recruiter_enums.py`

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T005 Create shared actor, optimistic-version and audit models in `backend/app/models/audit_event.py`
- [X] T006 Add recruiter API router aggregation in `backend/app/api/recruiter.py` and register it in `backend/app/main.py`
- [X] T007 [P] Add standard recruiter problem responses and pagination schemas in `backend/app/schemas/recruiter_common.py`
- [X] T008 [P] Add recruiter API client primitives, conflict handling and idempotency keys in `frontend/src/services/recruiterApi.js`
- [X] T009 Add reusable loading, empty, error and stale-result UI states in `frontend/src/components/recruiter/WorkspaceStates.jsx`
- [X] T010 Add migration and compatibility integration tests in `backend/tests/integration/test_recruiter_migrations.py`

## Phase 3: User Story 1 — Reliable screening criteria (Priority: P1) 🎯 MVP

**Goal**: Publish immutable criteria versions, enforce 100% weights, identify mandatory gates and keep simulated scores separate from official evaluations.

**Independent Test**: Publish a valid version, reject an invalid total, simulate alternate weights without changing official scores, then publish a new version and observe stale prior results.

- [X] T011 [P] [US1] Add criteria contract tests in `backend/tests/contract/test_criteria_api.py`
- [X] T012 [P] [US1] Add criteria validation and stale-evaluation unit tests in `backend/tests/unit/test_criteria_service.py`
- [X] T013 [US1] Create CriteriaSet and Criterion models in `backend/app/models/screening_criteria.py`
- [X] T014 [US1] Extend JobPosting and ScreeningResult compatibility fields in `backend/app/models/job_posting.py` and `backend/app/models/screening_result.py`
- [X] T015 [US1] Implement criteria draft/publish/backfill service in `backend/app/services/criteria_service.py`
- [X] T016 [US1] Implement criteria schemas and endpoints in `backend/app/schemas/screening_criteria.py` and `backend/app/api/criteria.py`
- [X] T017 [US1] Implement official versus simulated scoring in `backend/app/services/scoring_service.py`
- [X] T018 [US1] Build criteria editor with weight validation and version status in `frontend/src/components/recruiter/CriteriaEditor.jsx`
- [X] T019 [US1] Integrate criteria versions and simulation banner in `frontend/src/pages/RecruiterDashboard.jsx`

## Phase 4: User Story 2 — Resilient batch intake (Priority: P1)

**Goal**: Upload at least 200 CVs with item-level progress, dedupe warnings, reload recovery and retry.

**Independent Test**: Upload a mixed batch containing valid, corrupt, image-only and duplicate PDFs; successful files complete while failures remain retryable.

- [X] T020 [P] [US2] Add batch state-machine and dedupe unit tests in `backend/tests/unit/test_upload_batch_service.py`
- [X] T021 [P] [US2] Add batch API/reload/retry integration tests in `backend/tests/integration/test_upload_batches.py`
- [X] T022 [US2] Create UploadBatch, UploadItem and DuplicateMatch models in `backend/app/models/upload_batch.py`
- [X] T023 [US2] Implement hashing, dedupe and per-item processing in `backend/app/services/upload_batch_service.py`
- [X] T024 [US2] Implement batch create/status/events/retry endpoints in `backend/app/api/upload_batches.py`
- [X] T025 [US2] Build persistent batch uploader and item progress panel in `frontend/src/components/recruiter/BatchUploader.jsx`
- [X] T026 [US2] Add duplicate-resolution and retry interactions in `frontend/src/components/recruiter/BatchReviewPanel.jsx`

## Phase 5: User Story 3 — Evidence-backed candidate review (Priority: P1)

**Goal**: Present structured profile data, four-state criteria results, confidence and source evidence beside the original CV.

**Independent Test**: Open an evaluated candidate and verify important conclusions navigate to evidence while low-confidence/missing data is explicitly marked.

- [X] T027 [P] [US3] Add evidence mapping and no-evidence unit tests in `backend/tests/unit/test_evidence_service.py`
- [X] T028 [P] [US3] Add candidate detail/resume authorization contract tests in `backend/tests/contract/test_candidate_detail_api.py`
- [X] T029 [US3] Create CandidateApplication, Evaluation, CriterionResult and Evidence models in `backend/app/models/candidate_evaluation.py`
- [X] T030 [US3] Implement evidence extraction and legacy evaluation adapter in `backend/app/services/evidence_service.py`
- [X] T031 [US3] Implement candidate detail and audited original-resume endpoints in `backend/app/api/candidates.py`
- [X] T032 [US3] Replace candidate modal with split evidence/CV drawer in `frontend/src/components/recruiter/CandidateReviewDrawer.jsx`

## Phase 6: User Story 4 — Filtering and bulk operations (Priority: P2)

**Goal**: Server-side triage, configurable/saved views, cross-page selection and safe bulk actions.

**Independent Test**: Filter 500 candidates, save the view, select 20 across pages and execute a bulk stage/tag action with per-item outcomes.

- [X] T033 [P] [US4] Add candidate query performance and filter integration tests in `backend/tests/integration/test_candidate_query.py`
- [X] T034 [P] [US4] Add bulk idempotency/conflict tests in `backend/tests/integration/test_bulk_actions.py`
- [X] T035 [US4] Create SavedView, Tag and BulkAction models in `backend/app/models/recruiter_productivity.py`
- [X] T036 [US4] Implement indexed candidate query/facets in `backend/app/repositories/candidate_query_repository.py`
- [X] T037 [US4] Implement saved-view and bulk-action endpoints in `backend/app/api/recruiter_productivity.py`
- [X] T038 [US4] Rebuild candidate table with server pagination and column chooser in `frontend/src/components/recruiter/CandidateGrid.jsx`
- [X] T039 [US4] Add cross-page selection and bulk action bar in `frontend/src/components/recruiter/BulkActionBar.jsx`

## Phase 7: User Story 5 — Pipeline and decision history (Priority: P2)

**Goal**: Track recruiter decisions, required reject reasons, notes and an append-only timeline without overwriting AI recommendations.

**Independent Test**: Advance and reject candidates, trigger a concurrent edit conflict and reconstruct all actor/time/reason changes from the timeline.

- [X] T040 [P] [US5] Add pipeline transition and decision audit tests in `backend/tests/integration/test_decisions.py`
- [X] T041 [US5] Create decision event model and application projection updater in `backend/app/models/recruitment_decision.py` and `backend/app/services/decision_service.py`
- [X] T042 [US5] Implement optimistic decision/note endpoints in `backend/app/api/decisions.py`
- [X] T043 [US5] Build pipeline control, reject dialog and timeline in `frontend/src/components/recruiter/DecisionPanel.jsx`

## Phase 8: User Story 6 — Finalist comparison (Priority: P2)

**Goal**: Compare two to five candidates evaluated against the same criteria version.

**Independent Test**: Compare three finalists and see aligned criteria, evidence, notes and UNKNOWN values without false fail states.

- [X] T044 [P] [US6] Add same-version comparison contract tests in `backend/tests/contract/test_comparison_api.py`
- [X] T045 [US6] Implement comparison query/service/endpoint in `backend/app/services/comparison_service.py` and `backend/app/api/comparisons.py`
- [X] T046 [US6] Build comparison matrix UI in `frontend/src/components/recruiter/CandidateComparison.jsx`

## Phase 9: User Story 7 — Analytics and collaboration basics (Priority: P3)

**Goal**: Show stage funnel, upload quality, processing time and AI override rate for a job.

**Independent Test**: Seed decision/batch history and verify all dashboard aggregates match source records.

- [X] T047 [P] [US7] Add analytics aggregation tests in `backend/tests/integration/test_recruiter_analytics.py`
- [X] T048 [US7] Implement analytics repository and endpoint in `backend/app/repositories/recruiter_analytics_repository.py` and `backend/app/api/recruiter_analytics.py`
- [X] T049 [US7] Build recruiter funnel and quality metrics in `frontend/src/components/recruiter/RecruiterAnalytics.jsx`

## Phase 10: Polish & Cross-Cutting Concerns

- [X] T050 Add access policy, export/view audit and anonymization flow in `backend/app/services/candidate_privacy_service.py`
- [X] T051 [P] Add accessibility and responsive interaction tests in `frontend/tests/e2e/recruiter-workspace.spec.js`
- [X] T052 Add legacy backfill/rollout feature flag and release notes in `backend/app/core/migrations.py` and `specs/003-recruiter-workspace-upgrade/quickstart.md`
- [X] T053 Run all automated tests and the three acceptance journeys in `specs/003-recruiter-workspace-upgrade/quickstart.md`

## Dependencies & Execution Order

- Phase 1 → Phase 2 → all user stories.
- US1 is the MVP and supplies versioned criteria to US3 and US6.
- US2 can proceed after foundation; auto-evaluation pins a published US1 criteria version.
- US3 consumes US1 criteria and existing/new resume sources.
- US4 depends on CandidateApplication/Evaluation projections from US3.
- US5 depends on CandidateApplication and feeds US6/US7.
- US6 depends on US1, US3 and US5. US7 depends on US2 and US5 histories.
- Phase 10 follows the stories selected for release.

## Parallel Opportunities

- T003/T004, T007/T008, and test tasks marked `[P]` touch independent files.
- After Phase 2, US1 model/service work and US2 batch model/service work can be developed independently, but this repository executes them sequentially unless a team is assigned.
- Frontend components can begin once their corresponding API schemas stabilize.

## Implementation Strategy

1. Ship Setup + Foundation with compatibility tests.
2. Deliver US1 as the first MVP: trustworthy criteria and official/simulated scoring.
3. Add US2 and US3 to complete the trustworthy screening loop.
4. Add productivity and decision layers (US4–US6).
5. Add analytics, privacy hardening and rollout checks.

Every completed task is marked `[X]`; commit after each logical vertical slice.
