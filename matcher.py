"""Lightweight resume/job-description matching for a portfolio prototype.

Scores are heuristic ranking signals, not validated hiring recommendations.
Keep a human reviewer in the decision loop.
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

JOB_DESCRIPTIONS = [
    {
        "title": "Data Analyst",
        "description": "Analyze data, build reports and dashboards, validate data quality, use SQL, Excel, Python and business intelligence tools.",
        "required_skills": ["SQL", "Excel", "Power BI", "Python", "Data Analysis"],
        "min_experience": 0,
    },
    {
        "title": "Python Developer",
        "description": "Build Python applications and APIs, write maintainable code, work with databases, testing and software development.",
        "required_skills": ["Python", "Flask", "SQL", "Git", "REST API"],
        "min_experience": 1,
    },
    {
        "title": "Machine Learning Analyst",
        "description": "Explore datasets, build machine learning workflows, evaluate models and communicate analytical results.",
        "required_skills": ["Python", "Machine Learning", "pandas", "scikit-learn", "Statistics"],
        "min_experience": 1,
    },
]

SKILL_TAXONOMY = sorted({
    skill for job in JOB_DESCRIPTIONS for skill in job["required_skills"]
} | {"PostgreSQL", "MySQL", "Excel", "Power BI", "DAX", "Tableau", "NumPy",
     "pandas", "Matplotlib", "Seaborn", "Data Validation", "Data Cleaning",
     "Communication", "Problem Solving", "Java", "JavaScript", "HTML", "CSS"})


def _normalise(values):
    return {str(value).strip().casefold(): str(value).strip()
            for value in (values or []) if str(value).strip()}


class ResumeMatcher:
    """In-memory matcher used by the demo Flask API."""

    def __init__(self):
        self.candidates = []

    def get_job_descriptions(self):
        return JOB_DESCRIPTIONS

    def parse_resume_text(self, resume_text):
        text = str(resume_text or "")
        lower = text.casefold()
        skills = [skill for skill in SKILL_TAXONOMY if skill.casefold() in lower]
        email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
        phone = re.search(r"(?:\+?\d[\d ()-]{7,}\d)", text)
        exp = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text, re.I)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return {
            "name": lines[0][:120] if lines else "",
            "email": email.group(0) if email else None,
            "phone": phone.group(0) if phone else None,
            "skills": skills,
            "experience": float(exp.group(1)) if exp else 0.0,
            "education": next((line for line in lines if any(
                term in line.casefold() for term in
                ("bachelor", "master", "b.tech", "mca", "bca", "degree")
            )), None),
            "note": "Rule-based extraction; verify all fields manually.",
        }

    def compute_match_score(self, candidate_name, candidate_skills,
                            experience_years, resume_text=""):
        candidate_map = _normalise(candidate_skills)
        candidate_skill_names = list(candidate_map.values())
        resume_text = str(resume_text or "")
        candidate_text = " ".join(candidate_skill_names) + " " + resume_text
        results = []

        for job in JOB_DESCRIPTIONS:
            required = job["required_skills"]
            required_map = _normalise(required)
            matched = [v for k, v in required_map.items() if k in candidate_map]
            missing = [v for k, v in required_map.items() if k not in candidate_map]
            skill_score = len(matched) / len(required_map) if required_map else 0.0
            try:
                matrix = TfidfVectorizer(ngram_range=(1, 2), max_features=5000).fit_transform(
                    [job["description"], candidate_text]
                )
                text_score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])
            except ValueError:
                text_score = 0.0
            required_exp = float(job.get("min_experience", 0))
            experience = max(0.0, float(experience_years or 0))
            if required_exp == 0 or experience >= required_exp:
                exp_score = 1.0
            elif experience >= required_exp - 1:
                exp_score = 0.6
            elif experience >= required_exp - 2:
                exp_score = 0.3
            else:
                exp_score = 0.1
            score = round((text_score * 0.45 + skill_score * 0.40 + exp_score * 0.15) * 100, 2)
            results.append({
                "job_matched": job["title"], "match_score": score,
                "tfidf_similarity": round(text_score, 4),
                "skill_overlap": round(skill_score, 4),
                "experience_score": exp_score,
                "matched_skills": matched, "missing_skills": missing,
            })

        best = max(results, key=lambda item: item["match_score"])
        score = best["match_score"]
        status = "shortlisted" if score >= 65 else ("under_review" if score >= 40 else "review_required")
        result = {
            "candidate_name": str(candidate_name or "Unknown"),
            "experience_years": max(0.0, float(experience_years or 0)),
            **best,
            "status": status,
            "decision_note": "Prototype score only; not a hiring decision. Human review is required.",
        }
        self.candidates.append(result)
        return result

    def get_all_candidates(self):
        return list(self.candidates)

    def shortlist(self, threshold=65):
        threshold = float(threshold)
        return [candidate for candidate in self.candidates
                if candidate.get("match_score", 0) >= threshold]
