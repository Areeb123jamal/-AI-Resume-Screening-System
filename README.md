# AI Resume Screening System

A Python project exploring resume parsing and job-description matching. The repository includes an application, matching logic, job-description data, and supporting documentation.

## What it does
The documented workflow describes:
- Resume input and file validation
- Text extraction and normalization
- Extraction of candidate details and skills
- Comparison between resume content and a job description
- A weighted matching score based on text similarity, skill overlap, and experience matching

See the project documentation and source files for the implemented behavior and current limitations.

## Repository contents
- `app.py` — application entry point
- `matcher.py` — matching logic
- `job_descriptions.json` — sample job-description data
- `flow_definition.md` — processing flow documentation
- `docs/` and `download/` — supporting project materials

## Getting started
1. Clone the repository.
2. Inspect `app.py` and the project documentation to identify dependencies and configuration.
3. Install the dependencies required by the code.
4. Configure any required environment variables locally; never commit credentials or personal resume data.
5. Run the application using the instructions and entry points defined in the source.

## Important considerations
This is a portfolio project, not a validated hiring decision system. Resume parsing and keyword matching can be inaccurate, and scores can reflect bias or missing context. Use human review, test with representative examples, protect candidate data, and do not automatically reject candidates solely on the basis of a model score.

## Suggested next steps
- Add a pinned dependency file and exact run instructions.
- Include synthetic test resumes and expected outputs.
- Evaluate parsing and matching errors with a documented test set.
- Explain score calibration and fairness limitations.
- Add a demo screenshot or short walkthrough after verifying the app runs.
