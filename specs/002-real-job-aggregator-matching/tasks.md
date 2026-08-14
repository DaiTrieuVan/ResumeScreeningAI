# Tasks: Real Job Aggregator & Candidate AI Matcher

**Input**: Design documents from [`specs/002-real-job-aggregator-matching/`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/)
**Prerequisites**: [`plan.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/plan.md), [`spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/spec.md), [`data-model.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/data-model.md)

---

## Phase 1: Setup & Data Models

- [x] T001 [P] Create `RealJobPosting` and `CandidateJobMatch` SQLAlchemy ORM models in `backend/app/models/real_job.py`
- [x] T002 [P] Create Pydantic DTO schemas for Real Job listings and CV Matching in `backend/app/schemas/real_job.py`

---

## Phase 2: Foundational Aggregator & Seeder Service (US1)

- [x] T003 Implement Real Job Aggregator & Seeder service (TopCV & ITViec connectors with sample tech job feeds) in `backend/app/services/job_aggregator.py`
- [x] T004 Implement Real Job query and sync API endpoints in `backend/app/api/real_jobs.py`

---

## Phase 3: Reverse CV-to-Jobs Two-Stage AI Engine (US2 - MVP) 🎯

- [x] T005 Implement Reverse CV-to-Jobs Vector Shortlisting + Gemini 1.5 Flash structured job match reranker in `backend/app/services/cv_job_matcher.py`
- [x] T006 Implement CV-to-Real-Jobs Match endpoint (`POST /api/real-jobs/match`) in `backend/app/api/real_jobs.py`

---

## Phase 4: Frontend Candidate Job Search Portal (US2 & US3)

- [x] T007 [P] Build Real Job Card component with Match Score %, TopCV/ITViec badges, salary, location & apply link in `frontend/src/components/RealJobCard.jsx`
- [x] T008 [P] Build Real Job Filters component (Match Score threshold slider, Location, Min Salary, Skill tags) in `frontend/src/components/RealJobFilters.jsx`
- [x] T009 Assemble Candidate Real Jobs Portal page in `frontend/src/pages/RealJobsPortal.jsx`
- [x] T010 Add "Tìm Việc Thật (TopCV / ITViec)" navigation tab in `frontend/src/components/Navbar.jsx` and `frontend/src/App.jsx`

---

## Phase 5: Verification & End-to-End Validation

- [x] T011 Write backend API integration test for real job matching in `backend/tests/test_real_jobs_api.py`
- [x] T012 Validate end-to-end CV upload to Real Jobs matching flow according to `quickstart.md`
