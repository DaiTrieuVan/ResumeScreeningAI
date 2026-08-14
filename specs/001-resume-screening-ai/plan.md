# Implementation Plan: Resume Screening AI

**Branch**: `001-resume-screening-ai` | **Date**: 2026-08-09 | **Spec**: [spec.md](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/spec.md)

**Input**: Feature specification from [`specs/001-resume-screening-ai/spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/spec.md)

---

## Summary

Build a high-performance Resume Screening & AI Matching web application featuring a two-stage evaluation engine (Stage 1: embedding vector similarity shortlist; Stage 2: Gemini 1.5 Flash structured reranker) with an interactive recruiter dashboard (real-time slider score adjustments, bulk upload, CSV/PDF export) and a candidate-facing Career Gap Advisor.

---

## Technical Context

- **Language/Version**: Python 3.13
- **Backend Framework**: FastAPI (0.115+) with Pydantic v2 & SQLAlchemy 2.0 (Async)
- **Primary AI/LLM Provider**: Google Gemini 1.5 Flash via `google-genai` SDK with Structured JSON Schema output
- **Document Parsing**: `pdfplumber` for PDF text stream extraction + regex/text sanitizer for mixed Vietnamese/English text
- **Vector Search / Embedding**: In-memory NumPy Cosine Similarity over Gemini `text-embedding-004` (or `all-MiniLM-L6-v2`) embeddings
- **Database / Storage**: SQLite (via `aiosqlite` ORM) + Local File Storage (`./storage/resumes/`)
- **Frontend Stack**: React 18 + Vite + Vanilla CSS (Glassmorphism & dark/light dynamic theme)
- **Testing Framework**: `pytest` + `pytest-asyncio` + `httpx` for API testing
- **Target Platform**: Desktop Web Browser (Web App with FastAPI backend + Vite React frontend)
- **Performance Targets**: Batch processing of 50 resumes in < 3 minutes (async concurrent LLM batching); dashboard filter response < 500ms; candidate gap analysis < 30s

---

## Constitution Check

- **Architecture Rules**: Clean Layered Architecture (`Controller/API` -> `Service/Domain` -> `Repository/DB/AI`).
- **Security & Data Handling**: Input validation, sanitized upload handling, deferred PII anonymization toggle hook.
- **Error Handling**: Graceful per-file failure handling during batch resume parsing without halting overall process.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-resume-screening-ai/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technology choices & architectural decisions
├── data-model.md        # Database schema & entity models
├── quickstart.md        # Validation & local run guide
└── contracts/           # API schemas & endpoint contracts
    └── screening-api.yaml
```

### Proposed Source Code Layout

```text
backend/
├── app/
│   ├── api/             # API routes & endpoint handlers (FastAPI)
│   ├── core/            # Config, security, database session
│   ├── models/          # DB ORM models (SQLAlchemy / SQLModel)
│   ├── schemas/         # Request / Response Pydantic DTOs
│   ├── services/        # Business logic & AI pipelines (Parser, Embedding, Reranker)
│   └── repositories/    # Database queries & data access
├── tests/
│   ├── unit/
│   └── integration/
└── requirements.txt

frontend/
├── src/
│   ├── components/      # UI components (Upload, CandidateTable, MatchModal)
│   ├── pages/           # RecruiterDashboard, JobPostingView, GapAdvisorView
│   ├── services/        # API client services
│   └── styles/          # Design system & CSS
├── package.json
└── vite.config.js
```

**Structure Decision**: Web Application layout (`backend/` + `frontend/`).

---

## Complexity Tracking

| Requirement / Component | Risk / Bottleneck | Mitigation Strategy |
| :--- | :--- | :--- |
| Batch LLM Reranking (50 resumes) | Rate limits & API latency | Async batching + concurrent worker queue (e.g. asyncio / celery / background tasks) |
| Mixed Vietnamese / English PDF extraction | Bad OCR / encoding issues | Plain-text PDF stream parsing via `pdfplumber` with fallback cleanup |