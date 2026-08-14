# Feature Specification: Real Job Aggregator & Candidate AI Matcher

**Feature Branch**: `002-real-job-aggregator-matching`

**Created**: 2026-08-09

**Status**: Draft

**Input**: User description: "Lấy dữ liệu về Jobs thật từ các trang web xin việc như TopCV, ITViec; ứng viên có thể lọc và tìm việc trực tiếp dựa trên CV đã upload"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real Job Feed Ingestion & Normalization (Priority: P1)

As a System Admin / Candidate, I want the system to aggregate real job listings from job portals (TopCV, ITViec) and normalize them into a standard schema (Title, Company, Required Skills, Salary Range, Job Description, Apply Link) so that candidate CVs can be matched against real hiring opportunities.

**Why this priority**: Foundational data layer. Real job matching cannot operate without a searchable pool of normalized real-world job postings.

**Independent Test**: Can be tested independently by running the job aggregator service (or seeding sample TopCV/ITViec job feeds), and verifying that job records are correctly stored with extracted skills, salary, location, and apply URLs.

**Acceptance Scenarios**:

1. **Given** real job listings from TopCV / ITViec sources, **When** the aggregator runs, **Then** jobs are stored with structured fields: Job Title, Company Name, Required Skills Array, Location, Salary, Full Description, and Original Source URL.
2. **Given** duplicate job listings across sources, **When** aggregated, **Then** the system deduplicates records based on Company Name + Job Title similarity.

---

### User Story 2 - Automated CV-to-Jobs AI Matcher & Search (Priority: P1) 🎯 MVP

As a Job Seeker, I want to upload my CV (PDF) so that the system automatically scans all active real jobs, calculates an AI Match Score (0–100%) for each job, and displays a ranked list of top job recommendations tailored to my profile.

**Why this priority**: Primary candidate-facing value proposition. Enables candidates to instantly find the best real job openings matching their exact skills and experience.

**Independent Test**: Upload a candidate CV, trigger "Find Matching Jobs", and verify that the system returns real job postings ordered by AI Match Score with match explanations.

**Acceptance Scenarios**:

1. **Given** an uploaded candidate CV, **When** the candidate clicks "Find Matching Jobs", **Then** Stage 1 vector search pre-ranks top N relevant jobs, and Stage 2 Gemini AI reranks them to output an overall Match Score (0–100%), matched skills, and key gaps for each real job.
2. **Given** a list of matched real jobs, **When** the candidate clicks on a job card, **Then** the system displays the side-by-side match breakdown (Why you're a fit, missing skills to learn) and a direct link to "Apply on TopCV / ITViec".

---

### User Story 3 - Interactive Real Job Filter & Salary / Location Search (Priority: P2)

As a Job Seeker, I want to filter matched real jobs by Match Score (e.g. ≥ 80%), Location (Hà Nội, TP.HCM, Da Nang, Remote), Min Salary, and Specific Skill Tags so I can quickly narrow down target opportunities.

**Why this priority**: Essential for user experience, allowing candidates to personalize search criteria based on location and compensation preferences.

**Independent Test**: Filter candidate match results by "Min Score: 80%" and "Location: TP.HCM", verifying that only jobs meeting both criteria are displayed.

**Acceptance Scenarios**:

1. **Given** candidate match results, **When** the user applies a filter for "Score ≥ 75%" and "Location: Remote / TP.HCM", **Then** the list updates in real-time without re-running LLM calls.
2. **Given** a job of interest, **When** the candidate clicks "Save to Shortlist", **Then** the job is saved to their candidate profile for quick reference later.

---

### Edge Cases

- What happens when external job portal websites change HTML structure or block scrapers (rate limiting / CAPTCHA)?
- How does the system process job listings with vague salary descriptions (e.g., "Thỏa thuận" / "Negotiable")?
- What happens when a candidate CV has very low similarity (< 30%) with all active job listings?
- How does the system handle expired or closed job listings from TopCV / ITViec?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a Job Aggregator service capable of ingesting and parsing job listings from TopCV and ITViec data feeds/APIs into a unified schema.
- **FR-002**: System MUST extract and normalize key job fields: Title, Company Name, Industry, Location (Hanoi, HCMC, Danang, Remote), Salary Range (Min/Max/Currency or Negotiable), Required Skills, Preferred Skills, Experience Required, Full JD Text, and Source URL.
- **FR-003**: System MUST execute the Two-Stage AI Matching Engine over active real jobs when a candidate requests job recommendations:
  - *Stage 1*: Vector embedding similarity search (`all-MiniLM-L6-v2` / `text-embedding-004`) to retrieve top 30 job candidates.
  - *Stage 2*: Gemini 1.5 Flash structured rerank to compute Job Match Score (0–100%), matched skills, and fit explanation.
- **FR-004**: System MUST allow candidates to filter real job match results by minimum match score, salary range, location, and required skill tags.
- **FR-005**: System MUST provide direct external redirection links to original job postings ("Apply on TopCV", "Apply on ITViec").
- **FR-006**: System MUST handle unparseable or expired job URLs gracefully by marking job status as `EXPIRED` or `INACTIVE`.

### Key Entities

- **RealJobPosting**: Represents an aggregated real job listing from TopCV/ITViec. Attributes: Source (`TopCV`, `ITViec`), External ID, Title, Company Name, Location, Salary Range Text, Salary Min/Max, Required Skills Array, Experience Required, Full JD Text, Source URL, Status (`ACTIVE`, `EXPIRED`), Aggregated At.
- **CandidateJobMatch**: Represents the evaluation of a Candidate Resume against a RealJobPosting. Attributes: Resume ID, RealJob ID, Match Score (0-100), Skills Match %, Experience Match %, Strengths Summary, Gaps Summary, Match Reasoning, Saved Status (`SAVED`, `APPLIED`, `DEFAULT`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Candidate CV-to-Jobs matching returns top 20 matched real jobs with full AI reasoning in under 15 seconds.
- **SC-002**: Real Job Aggregator extracts skills and structured fields from TopCV/ITViec job postings with ≥ 85% accuracy.
- **SC-003**: Interactive job filtering (by score threshold, salary, location) responds in under 300 milliseconds.

## Assumptions

- Aggregation leverages official APIs, RSS feeds, or structured web scraping pipelines with appropriate rate limits.
- Target job sources are primarily Vietnam-based IT & Tech job portals (TopCV, ITViec, VietnamWorks).
- Salary normalization parses both VND (Triệu VNĐ) and USD ranges into standard numeric min/max values for filtering.
