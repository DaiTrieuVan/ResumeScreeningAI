# Implementation Plan: Real Job Aggregator & Candidate AI Matcher

**Branch**: `002-real-job-aggregator-matching` | **Date**: 2026-08-09 | **Spec**: [spec.md](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/spec.md)

**Input**: Feature specification from [`specs/002-real-job-aggregator-matching/spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/spec.md)

---

## Summary

Build a Real Job Aggregator service and CV-to-Jobs AI Matcher that continuously ingests real tech job listings from TopCV and ITViec, normalizes them into structured job records (Title, Company, Location, Salary, Required Skills, Apply URL), and allows candidates to upload their CV to automatically scan, match, and rank real hiring opportunities with detailed Gemini AI match reasoning.

---

## Technical Context

- **Language/Version**: Python 3.13
- **Backend Framework**: FastAPI (0.115+) + Pydantic v2 + SQLAlchemy 2.0 (Async ORM)
- **Aggregator / Scraper**: `httpx` + `BeautifulSoup4` / RSS feeds for TopCV & ITViec job normalization
- **Primary AI/LLM Provider**: Google Gemini 1.5 Flash via `google-genai` SDK
- **Vector Search / Embedding**: In-memory NumPy Cosine Distance / `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Database / Storage**: SQLite (`aiosqlite`)
- **Frontend Stack**: React 18 + Vite + Vanilla CSS (Glassmorphism UI)
- **Target Platform**: Web Application (Recruiter Workspace + Candidate Job Search Portal)
- **Performance Targets**: CV-to-Jobs match ranking < 15 seconds; real-time job filter response < 300ms

---

## Constitution Check

- **Layered Architecture**: `api/real_jobs.py` -> `services/job_aggregator.py` & `services/cv_job_matcher.py` -> `models/real_job.py`.
- **Deduplication & Anti-Scrape Protection**: Normalizes titles and company names to prevent duplicate job records; respects rate limits.
- **External Redirection**: Provides clean, direct affiliate/source links ("Ứng tuyển trên TopCV", "Ứng tuyển trên ITViec").

---

## Project Structure

```text
backend/app/
├── api/
│   └── real_jobs.py             # API endpoints (/api/real-jobs, /api/real-jobs/match)
├── models/
│   └── real_job.py              # RealJobPosting & CandidateJobMatch SQLAlchemy models
├── schemas/
│   └── real_job.py              # Pydantic DTOs
└── services/
    ├── job_aggregator.py        # TopCV & ITViec ingestion & normalization service
    └── cv_job_matcher.py        # Two-stage CV-to-Jobs vector search + Gemini rerank service

frontend/src/
├── components/
│   ├── RealJobCard.jsx          # Job card displaying Match Score %, salary, location & apply link
│   └── RealJobFilters.jsx       # Location, salary min, score threshold, and skill filters
└── pages/
    └── RealJobsPortal.jsx       # Candidate Real Job Finder page
```

---

## Complexity Tracking

| Component | Risk / Bottleneck | Mitigation Strategy |
| :--- | :--- | :--- |
| Large Real Job Pool (1,000+ jobs) | LLM latency if reranking all jobs | Stage 1 Vector Pre-Ranking filters top 25 jobs before Gemini Stage 2 Rerank |
| Diverse Salary Formats ("20-30 Triệu", "$1500", "Thỏa thuận") | Regex parsing errors | Custom Salary Normalizer parsing numeric Min/Max bounds for filtering |
