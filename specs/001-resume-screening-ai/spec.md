# Feature Specification: Resume Screening AI

**Feature Branch**: `001-resume-screening-ai`

**Created**: 2026-08-09

**Updated**: 2026-08-09

**Status**: Draft

**Input**: User description: "Define feature specifications for Resume Screening AI Project"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Job Requirements Setup & Automated Resume Matching (Priority: P1)

As a Recruiter or Hiring Manager, I want to create a Job Posting with defined skills and experience requirements, and upload candidate resumes (PDF) so that the AI automatically parses, scores, and ranks candidates based on match relevance.

**Why this priority**: Core value proposition of the system. Without job setup, resume parsing, and matching, the screening tool cannot function.

**Independent Test**: Can be tested independently by uploading a Job Description and 5 sample resumes, then verifying that each candidate receives a candidate profile, overall match score (0-100%), and rank order.

**Acceptance Scenarios**:

1. **Given** a recruiter creates a job description with required skills (e.g., Python, PostgreSQL, REST APIs) and minimum 3 years experience, **When** resumes in PDF format are uploaded in bulk, **Then** the system extracts key candidate data (name, contact, skills, years of experience) and displays them in a structured table.
2. **Given** uploaded resumes and job requirements, **When** AI screening runs, **Then** each candidate receives a calculated match score (0-100%), match breakdown (skills match %, experience fit, education fit), and key strengths/gaps summary.
3. **Given** unsupported or corrupted file formats (e.g., password-protected PDFs or image-only scans), **When** uploaded, **Then** the system flags the file with a clear processing error without halting the batch upload.

---

### User Story 2 - Interactive Candidate Review & Screening Dashboard (Priority: P2)

As a Recruiter, I want to view an interactive candidate dashboard where I can filter by match score, search skills, view detailed AI match reasoning, and update candidate status (Shortlisted, Under Review, Rejected).

**Why this priority**: High operational value for recruiters reviewing high volumes of candidates, enabling quick decision making.

**Independent Test**: Can be tested independently by loading pre-processed candidate results, applying filters (e.g., score > 80%), inspecting AI reasoning modal, and changing status.

**Acceptance Scenarios**:

1. **Given** a list of screened candidates, **When** the recruiter applies a filter for "Match Score ≥ 75%" and "Skill: Python", **Then** only matching candidates are displayed in real-time.
2. **Given** a selected candidate, **When** the recruiter opens the candidate detail view, **Then** the system displays the original resume side-by-side with the AI analysis (skill overlap, missing prerequisites, experience timeline).
3. **Given** a candidate profile, **When** the recruiter marks the status as "Shortlisted" or "Rejected", **Then** the candidate status updates immediately and is saved.

---

### User Story 3 - Batch Export & Recruiter Feedback Logging (Priority: P3)

As a Hiring Team Lead, I want to export shortlisted candidate summaries (CSV/PDF) and log feedback on AI scores so there is an auditable record of recruiter overrides for future reference.

**Why this priority**: Enables sharing results with hiring managers outside the portal and creates an audit trail of recruiter judgment vs. AI scoring.

**Independent Test**: Can be tested independently by selecting 3 shortlisted candidates, exporting a summary report, and submitting score feedback (+/- adjustment) that is persisted and retrievable.

**Acceptance Scenarios**:

1. **Given** a set of shortlisted candidates, **When** the recruiter clicks "Export Shortlist", **Then** a clean CSV/PDF document is generated containing candidate contact details, match scores, and key highlights.
2. **Given** an AI match score, **When** a recruiter overrides or adjusts the score with feedback (e.g., "candidate has relevant domain experience not captured"), **Then** the system logs recruiter feedback (score delta, free-text note, timestamp, recruiter ID) against that Screening Result for auditability.

**Out of scope for v1**: Automatic recalibration of AI scoring based on accumulated feedback. Feedback is stored for manual review and future iteration only, and does not change how future candidates are scored within v1.

---

### User Story 4 - Candidate Career Gap Advisor (Priority: P2)

As a Job Seeker, I want to submit my CV against a target Job Description and receive a gap analysis (missing skills, missing experience) with concrete suggestions on what to learn or add, so I can improve my fit for that role.

**Why this priority**: Second primary use case of the product alongside recruiter screening — serves an individual candidate directly, and is required for the product's full scope.

**Independent Test**: Can be tested independently by submitting one CV and one target JD as a standalone (non-recruiter) user, and verifying the output contains a gap list and actionable suggestions, without needing a Job Posting record or recruiter dashboard.

**Acceptance Scenarios**:

1. **Given** a candidate uploads their CV and pastes/selects a target JD, **When** the analysis runs, **Then** the system returns a matched-skills list, a missing-skills/experience list, and a plain-language explanation of the gap.
2. **Given** a gap analysis result, **When** the candidate views it, **Then** the system suggests concrete next steps (e.g., specific skills, certifications, or types of experience to acquire) tied to the missing items.
3. **Given** the same CV and JD, **When** re-analyzed later after the candidate updates their CV, **Then** the system reflects the updated gap without requiring a recruiter account or Job Posting setup.

---

### Edge Cases

- What happens when a resume is unreadable (scanned image without text OCR layer)?
- How does the system handle resumes with missing contact details or ambiguous dates?
- What happens when a user uploads 100+ resumes simultaneously (high concurrency / rate limits)?
- How does the system process resumes or JDs that mix Vietnamese and English (common in local tech job postings, e.g., Vietnamese sentence structure with English technical terms)?
- What happens when the automated extraction or scoring step fails or times out for a specific file mid-batch?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support document ingestion for PDF resumes up to 10MB per file. DOCX and TXT support is out of scope for v1; may be added in a later phase.
- **FR-002**: System MUST extract structured data fields from resumes: Candidate Name, Email, Phone Number, Listed Skills, Work History (Company, Role, Duration), and Education.
- **FR-003**: System MUST compute an overall Job Match Score (0–100%) by first identifying the most relevant candidates for a job, then producing a final score with an accompanying explanation for each of those candidates.
- **FR-004**: System MUST provide plain-language AI match reasoning explaining why a candidate scored high or low, highlighting matched skills and identified missing requirements.
- **FR-005**: System MUST allow recruiters to filter candidates by minimum match score, specific skill keywords, candidate status, and experience level.
- **FR-006**: System MUST support batch operations: bulk file upload, bulk status changes (Shortlist / Reject), and export to CSV/PDF.
- **FR-007**: System MUST handle unparseable or corrupted files gracefully, recording file-level status errors without stopping batch processing.
- **FR-008**: System MUST support configurable weightings per Job Posting, allowing recruiters to adjust criterion sliders (Skills vs. Experience vs. Education) and see the overall match score recalculate accordingly, without needing to re-run the full screening.
- **FR-009** *(Future work, out of scope for v1)*: System MAY offer an interactive PII Anonymization Toggle (masking candidate name, gender, contact details) for bias-reduced initial screening. Deferred by product decision; not required for the September 2026 submission.
- **FR-010**: System MUST support a candidate-facing flow (Career Gap Advisor, see User Story 4) that runs CV-vs-JD analysis without requiring a Job Posting record, recruiter account, or dashboard context.

### Key Entities

- **Job Posting**: Represents a hiring requisition. Attributes: Title, Department, Required Skills, Preferred Skills, Min/Max Years Experience, Required Education, Status, Score Weighting Config (Skills/Experience/Education weights, default equal).
- **Candidate Resume**: Represents an uploaded candidate document. Attributes: File Name, File Path/URL, Raw Text, Parsed Profile (Name, Email, Phone, Skills Array, Experience Timeline, Education Array).
- **Screening Result**: Represents the AI evaluation of a candidate against a Job Posting. Attributes: Job ID, Resume ID, Overall Score (0-100), Skills Sub-score, Experience Sub-score, Education Sub-score, Strengths Summary, Gaps Summary, Recruiter Status (New, Shortlisted, Under Review, Rejected), Feedback Notes (score delta, text, timestamp, recruiter ID).
- **Gap Analysis**: Represents a candidate-initiated CV-vs-JD analysis. Attributes: Resume ID, Target JD (text or reference), Matched Skills, Missing Skills/Experience, Suggested Next Steps, Created At. Not linked to a Job Posting or recruiter workspace.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Recruiters can process and rank a batch of 50 candidate resumes for a job posting in under 3 minutes total processing time.
- **SC-002**: Candidate resume parsing achieves ≥ 90% accuracy on standard text-based PDF resumes (correctly extracting Name, Contact, Skills, and Work History).
- **SC-003**: 90% of recruiters rate AI match reasoning as clear, relevant, and actionable on candidate evaluation reports.
- **SC-004**: Screening dashboard filters respond in under 500 milliseconds when filtering datasets of up to 1,000 candidate profiles.
- **SC-005**: Candidates using the Career Gap Advisor (User Story 4) receive a gap analysis result in under 30 seconds for a single CV-JD pair.

## Assumptions

- Target users (recruiters, hiring managers, and job-seeking candidates) access the system via standard desktop web browsers.
- Resumes and Job Descriptions are primarily in **Vietnamese**, frequently mixed with English technical terms (reflecting the target job sources: TopCV, ITViec). Extraction and matching must handle this mixed-language pattern; full multi-language OCR beyond Vietnamese/English is out of scope for v1.
- v1 resume ingestion is **PDF-only**; DOCX/TXT support is a future enhancement, not a v1 requirement.
- Initial deployment uses a single-tenant or standard multi-tenant backend with standard cloud object storage for file uploads.
- Standard session-based or token authentication will protect all recruiter API endpoints. The Career Gap Advisor flow (User Story 4) does not require recruiter-level authentication, since it targets individual candidates.
- PII anonymization (FR-009) is explicitly deferred and will not be scoped into the v1 implementation plan or task breakdown.
- Feasibility of SC-001 (50 resumes in under 3 minutes) depends on implementation choices (e.g., how requests to the scoring engine are parallelized) that are addressed in the implementation plan, not in this specification.