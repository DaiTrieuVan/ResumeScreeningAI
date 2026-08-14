# Research & Architectural Decisions: Resume Screening AI

**Feature**: [`spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/spec.md)
**Plan**: [`plan.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/plan.md)

---

## 1. Document Parsing Strategy (PDF Ingestion)

- **Decision**: Use `pdfplumber` for PDF text extraction with custom UTF-8 text sanitization for mixed Vietnamese/English text.
- **Rationale**: Extracts text streams, layout blocks, and fonts directly from vector PDFs without external binary OCR dependencies.
- **Alternatives Considered**: PyPDF2 (poor layout handling), Tesseract OCR (excessive latency for native PDFs).

---

## 2. Two-Stage Matching Architecture

- **Stage 1 (Shortlisting & Fast Retrieval)**:
  - **Approach**: Embed job requirements and candidate resume text using `sentence-transformers` (`all-MiniLM-L6-v2`) or Gemini `text-embedding-004`. Compute Cosine Similarity to pre-rank candidates.
  - **Purpose**: Rapidly filter top candidates for detailed evaluation.

- **Stage 2 (LLM Reranking & Structured Evaluation)**:
  - **Approach**: Pass Job Description + Candidate Resume text to Gemini 1.5 Flash using Structured Outputs (JSON Schema constraint).
  - **Structured Output**:
    - `skills_score`: 0–100
    - `experience_score`: 0–100
    - `education_score`: 0–100
    - `strengths`: list of strings
    - `gaps`: list of strings
    - `reasoning`: text explanation
  - **Client-side / API Weighted Combination**:
    ```text
    overall_score = (skills_score * w_skills) + (experience_score * w_exp) + (education_score * w_edu)
    ```

---

## 3. Storage & Database Choice

- **Relational DB**: SQLite (`aiosqlite` + SQLAlchemy 2.0 Async ORM) for local zero-config deployment with full transactional integrity.
- **Vector Index**: In-memory NumPy vector matrix / SQLite Blob index.
- **File Storage**: Local filesystem storage at `./storage/resumes/`.

## 4. Frontend & User Interface Architecture

- **Stack**: [e.g., Vite + React + Vanilla CSS or Next.js]
- **Key Modules**:
  - `JobPostingManager`: Form to create/edit job requirements & slider weights.
  - `BatchResumeUploader`: Drag & drop multi-file PDF upload with progress bar.
  - `ScreeningDashboard`: Filterable data table (score, status, skills search) with instant score recalculation on slider change.
  - `CandidateDetailModal`: Side-by-side original PDF preview vs. AI reasoning breakdown.
  - `CareerGapAdvisor`: Candidate-facing single CV-vs-JD analysis tool.
