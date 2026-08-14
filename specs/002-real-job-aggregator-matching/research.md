# Research & Architecture Decisions: Real Job Aggregator & Candidate Matcher

**Feature**: [`spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/spec.md)
**Plan**: [`plan.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/plan.md)

---

## 1. Job Aggregation & Normalization Pipeline

- **Sources**: TopCV (Vietnam Tech jobs), ITViec (IT/Software roles), sample curated tech feeds.
- **Normalizer Rules**:
  - `salary_min_vnd`, `salary_max_vnd`: Extracted numeric values in VND (e.g. 20M - 35M -> 20,000,000 to 35,000,000).
  - `location_tag`: `HA_NOI`, `HO_CHI_MINH`, `DA_NANG`, `REMOTE`, `OTHER`.
  - `skills`: Normalized tech tags (`Python`, `React`, `FastAPI`, `Docker`, `PostgreSQL`, `Java`, `Vue`, etc.).

---

## 2. Reverse CV-to-Jobs Two-Stage Engine

- **Stage 1 (Vector Candidate Job Shortlist)**:
  - Input: Candidate CV Extracted Text.
  - Action: Compute Cosine Vector Similarity against all active `RealJobPosting` embedding vectors.
  - Output: Top 25 candidate jobs.

- **Stage 2 (Gemini 1.5 Flash Structured Job Matcher)**:
  - Input: CV Content + Top 25 Real Job Postings.
  - Structured Evaluation Schema:
    - `match_score`: 0–100
    - `why_you_fit`: list of strength bullet points
    - `skills_gaps`: list of missing required skills
    - `match_reasoning`: summary text
