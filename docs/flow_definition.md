# Resume Processing Flow — Design Notes

> **Status clarification:** This file preserves an inherited design document, not a description of the currently implemented application. The current Flask app accepts JSON text and candidate skills, uses basic regex-based text extraction and TF-IDF/skill-overlap scoring, and stores matches in process memory. PDF/DOCX upload parsing, spaCy NER, a production database, email notifications, and the performance targets below are **not implemented or verified** in the current source. Treat the following architecture as a proposed design only.

## Current implementation at a glance

1. `POST /match` accepts a candidate name, skill list, experience value, and optional resume text.
2. The prototype compares candidate text against three hard-coded example job descriptions.
3. A heuristic score combines TF-IDF text similarity, required-skill overlap, and a simple experience component.
4. The result is returned by the Flask API. Candidate results remain in memory and reset when the process restarts.
5. `POST /parse_resume` uses simple pattern matching; extracted details require human verification.

This is a learning prototype. Do not use scores as hiring decisions or automatically reject candidates. The scoring weights and thresholds have not been calibrated or evaluated for accuracy or fairness.

---

## Original proposed architecture (not implemented)

The following sections preserve the original technical plan for reference. They should not be read as evidence that these features exist in the current code.

# Resume Processing Flow Definition
## AI Resume Screening System — Technical Documentation

---

## Overview

This document defines the complete data flow for resume processing within the
AI Resume Screening System, from file upload through NLP parsing, ML scoring,
and final candidate status assignment.

---

## 1. End-to-End Flow Diagram

```
Candidate Submits Resume
          │
          ▼
┌─────────────────────┐
│  File Upload (API)  │  POST /match  or  POST /parse_resume
│  Accepted formats:  │  ─ PDF  ─ DOCX  ─ TXT  ─ JSON payload
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  File Validation    │  MIME-type check (not just extension)
│                     │  Max size: 5 MB
│                     │  Allowed: PDF, DOCX, TXT only
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Text Extraction    │  PDF  → PyMuPDF (fitz)
│                     │  DOCX → python-docx
│                     │  TXT  → direct read (UTF-8)
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  NLP Parsing Pipeline (spaCy en_core_web_lg)        │
│                                                     │
│  Step 1 — Text Normalisation                        │
│           Lowercase · whitespace strip · Unicode    │
│                                                     │
│  Step 2 — Named Entity Recognition (NER)            │
│           PERSON  → candidate name                  │
│           ORG     → companies / institutions        │
│           DATE    → employment / education periods  │
│           GPE     → location                        │
│                                                     │
│  Step 3 — Custom Regex Extractors                   │
│           Email   → RFC-5322 pattern                │
│           Phone   → +91-XXXXXXXXXX pattern          │
│           LinkedIn URL                              │
│                                                     │
│  Step 4 — Section Identification                    │
│           Pattern match on headers:                 │
│           EDUCATION · EXPERIENCE · SKILLS           │
│           PROJECTS · CERTIFICATIONS                 │
│                                                     │
│  Step 5 — Skills Extraction                         │
│           PhraseMatcher against 2 500-entry         │
│           SKILLS_TAXONOMY list                      │
│                                                     │
│  Step 6 — Experience Calculation                    │
│           Regex: "\d+ years?" → max value           │
│           OR: date range calculation from sections  │
└────────┬────────────────────────────────────────────┘
         │  Structured candidate profile dict
         ▼
┌─────────────────────────────────────────────────────┐
│  ML Ranking Engine (scikit-learn)                   │
│                                                     │
│  Input A: Job Description text                      │
│  Input B: Parsed resume text                        │
│                                                     │
│  Component 1 — TF-IDF Cosine Similarity  (×0.45)   │
│    TfidfVectorizer(max_features=10 000,             │
│                   ngram_range=(1,2),                │
│                   sublinear_tf=True)                │
│    cosine_similarity(jd_vector, resume_vector)      │
│                                                     │
│  Component 2 — Skill Overlap Score       (×0.40)   │
│    |candidate_skills ∩ required_skills|             │
│    ─────────────────────────────────────            │
│           |required_skills|                         │
│                                                     │
│  Component 3 — Experience Match Score    (×0.15)   │
│    years >= min_required  → 1.0                     │
│    years >= min_required-1→ 0.6                     │
│    years >= min_required-2→ 0.3                     │
│    years <  min_required-2→ 0.1                     │
│                                                     │
│  Final Score = (C1×0.45 + C2×0.40 + C3×0.15)×100  │
└────────┬────────────────────────────────────────────┘
         │  match_score (0–100 float)
         ▼
┌─────────────────────┐
│  Status Assignment  │
│                     │
│  ≥ 65  → Shortlisted│
│  40–64 → Under Review│
│  < 40  → Rejected   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  API Response JSON  │  Returns full result dict
│  + DB Storage       │  (PostgreSQL in production)
│  + Email Trigger    │  (Flask-Mail → SMTP)
└─────────────────────┘
```

---

## 2. Data Structures

### 2.1 Input Payload (POST /match)

```json
{
  "name"        : "Rahul Sharma",
  "skills"      : ["Python", "Flask", "SQL", "Machine Learning"],
  "experience"  : 3,
  "resume_text" : "Experienced Python developer with 3 years..."
}
```

### 2.2 Parsed Resume Profile (Internal)

```json
{
  "name"             : "Rahul Sharma",
  "email"            : "rahul.sharma42@gmail.com",
  "phone"            : "+91-9876543210",
  "extracted_skills" : ["Python", "Flask", "Sql", "Scikit-Learn"],
  "experience_years" : 3.0,
  "education"        : ["B.Tech"],
  "raw_word_count"   : 142
}
```

### 2.3 Match Result (POST /match Response)

```json
{
  "candidate_name"    : "Rahul Sharma",
  "match_score"       : 85.2,
  "skill_overlap"     : 0.857,
  "tfidf_similarity"  : 0.712,
  "experience_score"  : 1.0,
  "matched_skills"    : ["Python", "Flask", "Sql"],
  "missing_skills"    : ["Machine Learning"],
  "experience_years"  : 3.0,
  "status"            : "shortlisted",
  "job_matched"       : "Python Developer"
}
```

---

## 3. Scoring Formula

```
Final Score = (TF-IDF Cosine × 0.45
             + Skill Overlap  × 0.40
             + Exp Score      × 0.15) × 100
```

| Weight | Component        | Rationale                                      |
|--------|------------------|------------------------------------------------|
| 45 %   | TF-IDF Cosine    | Captures overall semantic alignment of text    |
| 40 %   | Skill Overlap    | Directly measures JD skill requirement match   |
| 15 %   | Experience Match | Ensures basic experience threshold compliance  |

---

## 4. Status Thresholds

| Score Range | Status       | Action                           |
|-------------|--------------|----------------------------------|
| 65 – 100    | Shortlisted  | Auto-advance to interview stage  |
| 40 – 64     | Under Review | Requires manual recruiter review |
| 0 – 39      | Rejected     | Auto-reject with email feedback  |

---

## 5. Processing Performance Targets

| Metric                        | Target     |
|-------------------------------|------------|
| Resume parse time (PDF)       | < 3 sec    |
| Match score computation       | < 2 sec    |
| API response time (P95)       | < 500 ms   |
| Batch (50 resumes)            | < 2 min    |

---

*Document Version: 1.0 | Last Updated: May 2024*
