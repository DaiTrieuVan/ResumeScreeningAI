# Data Model: Real Job Aggregator & AI Matcher

**Feature**: [`spec.md`](file:///D:/Resume%20Screening%20AI%20Project/specs/002-real-job-aggregator-matching/spec.md)

---

## 1. `RealJobPosting` Entity
```sql
CREATE TABLE real_job_postings (
    id VARCHAR(36) PRIMARY KEY,
    source VARCHAR(50) NOT NULL,            -- TopCV, ITViec, Manual Feed
    external_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_logo_url VARCHAR(512),
    location VARCHAR(255) NOT NULL,         -- Hà Nội, TP. Hồ Chí Minh, Remote, etc.
    location_tag VARCHAR(50) DEFAULT 'OTHER', -- HA_NOI, HO_CHI_MINH, DA_NANG, REMOTE
    salary_text VARCHAR(255),               -- "20 - 35 Triệu VNĐ", "$1500 - $2500"
    salary_min_vnd INT,
    salary_max_vnd INT,
    required_skills JSON NOT NULL,          -- ["Python", "FastAPI", "Docker"]
    experience_required VARCHAR(255),       -- "2-4 năm", "Senior"
    description_text TEXT NOT NULL,
    source_url VARCHAR(512) NOT NULL,       -- Direct TopCV / ITViec apply URL
    status VARCHAR(50) DEFAULT 'ACTIVE',    -- ACTIVE, EXPIRED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 2. `CandidateJobMatch` Entity
```sql
CREATE TABLE candidate_job_matches (
    id VARCHAR(36) PRIMARY KEY,
    resume_id VARCHAR(36) REFERENCES candidate_resumes(id),
    real_job_id VARCHAR(36) REFERENCES real_job_postings(id),
    match_score FLOAT NOT NULL,             -- Overall match score (0-100)
    skills_sub_score FLOAT,
    experience_sub_score FLOAT,
    strengths_summary JSON,                -- Key match points
    gaps_summary JSON,                     -- Missing skills
    match_reasoning TEXT,
    saved_status VARCHAR(50) DEFAULT 'DEFAULT', -- DEFAULT, SAVED, APPLIED
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resume_id, real_job_id)
);
```
