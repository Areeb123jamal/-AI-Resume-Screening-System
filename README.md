# AI Resume Screening System — Prototype

> **Status: prototype; not a validated hiring tool.** This repository contains an imported Flask API and a lightweight heuristic matching engine. Resume parsing is rule-based, scoring is unvalidated, and all candidate records are held in memory.

## What is included
- Flask endpoints for matching, parsing, listing in-memory candidates, shortlisting by a score threshold, and listing sample job descriptions.
- TF-IDF text similarity plus required-skill overlap and a simple experience component.
- A synthetic candidate-data generator for local experimentation.
- Example job descriptions and technical flow documentation.

## Important limitations
- Scores are heuristic and have not been calibrated against a representative evaluation set.
- Text similarity and keyword overlap can miss relevant experience or reproduce bias. Do not automatically reject candidates or make hiring decisions from these scores.
- Resume parsing is intentionally basic and can extract incorrect names, skills, education, or experience.
- Candidate state is in memory and resets when the server restarts; no production database is implemented.
- Use synthetic test data. Do not upload real resumes, personal contact details, or confidential employer data to a public repository.
- The original application source contains an attribution to Rahul Sharma. Verify provenance and permissions before presenting the code as wholly original work.

## Setup

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The local development server starts at `http://127.0.0.1:5000`.

## Example API requests

Health check:

```bash
curl http://127.0.0.1:5000/
```

Match a synthetic candidate:

```bash
curl -X POST http://127.0.0.1:5000/match \
  -H "Content-Type: application/json" \
  -d '{"name":"Sample Candidate","skills":["SQL","Excel","Power BI"],"experience":1,"resume_text":"Entry-level analyst with SQL, Excel and Power BI experience."}'
```

Parse sample resume text:

```bash
curl -X POST http://127.0.0.1:5000/parse_resume \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Sample Candidate\nsample@example.com\nSkills: SQL, Python, Excel\n1 year of experience\nBCA"}'
```

## Endpoints
- `GET /` — health check and endpoint list
- `POST /match` — score a candidate against the sample job descriptions
- `POST /parse_resume` — rule-based extraction from resume text
- `GET /candidates` — candidates stored in the current process
- `POST /shortlist` — filter current in-memory records by a chosen score threshold
- `GET /jobs` — sample job descriptions

## Project files
- `app.py` — Flask API
- `matcher.py` — scoring and basic parsing logic
- `data_generator.py` — synthetic candidate generator
- `job_descriptions.json` — human-readable sample job data
- `requirements.txt` — Python dependencies
- `docs/flow_definition.md` — documented intended processing flow
- `SCREENSHOTS.md` — notes on optional API screenshots
- `tests/test_app.py` — API smoke tests
- `.github/workflows/tests.yml` — GitHub Actions test workflow

## Next validation steps
1. Add automated tests for empty inputs, unknown skills, missing experience, and invalid request types.
2. Compare score outputs with manually reviewed synthetic cases.
3. Add input validation and request-size limits.
4. Review fairness, privacy, and security before any broader use.

This documentation describes intended behavior from source inspection. The project has not been independently run or tested in this environment.
