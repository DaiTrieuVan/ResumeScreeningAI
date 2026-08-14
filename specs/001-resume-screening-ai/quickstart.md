# Quickstart & End-to-End Validation Guide: Resume Screening AI

**Feature**: [`spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/spec.md)
**Plan**: [`plan.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/001-resume-screening-ai/plan.md)

---

## 1. Prerequisites & Environment Setup

- Python 3.11+ (or Python 3.13)
- Node.js 18+ (for frontend)
- Environment Variables (`.env`):
  ```env
  GEMINI_API_KEY=your_api_key_here
  PORT=8000
  ```

---

## 2. Backend Setup & Run

```bash
# Clone / navigate to root
cd backend

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```

---

## 3. Frontend Setup & Run

```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```

---

## 4. End-to-End Validation Scenarios

### Scenario A: Recruiter Batch Resume Screening (User Story 1 & 2)
1. Open Recruiter Dashboard at `http://localhost:5173`.
2. Create Job Posting: Title = "Senior Python Developer", Required Skills = `["Python", "FastAPI", "PostgreSQL"]`, Min Experience = `3 years`.
3. Upload 5 PDF resumes in bulk.
4. Verify table shows candidate name, parsed skills, overall score (0-100%), and AI match breakdown.
5. Filter by `Score ≥ 75%` and verify table updates instantly (< 500ms).
6. Adjust slider weights (Skills 70%, Exp 20%, Edu 10%) and verify overall scores recalculate immediately without calling LLM.

### Scenario B: Candidate Career Gap Advisor (User Story 4)
1. Navigate to `http://localhost:5173/gap-advisor`.
2. Paste Target Job Description text and upload single PDF resume.
3. Click "Analyze Career Gap".
4. Verify response contains matched skills, missing skills, and actionable next steps (< 30 seconds).
