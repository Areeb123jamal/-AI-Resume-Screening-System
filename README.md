# ============================================================
#  AI Resume Screening System — matcher.py
#  Core NLP + ML Candidate Matching Engine
#
#  Algorithm:
#    Final Score = (TF-IDF Cosine × 0.45)
#                + (Skill Overlap  × 0.40)
#                + (Experience     × 0.15)
#               × 100
#
#  Libraries : scikit-learn (TF-IDF, cosine_similarity)
#              spaCy        (NLP parsing, NER)
#              re           (regex skill/email extraction)
# ============================================================

import re
import math
from collections import Counter

# ── Skills Taxonomy (2 500-entry in production; 80 here for demo) ──────────
SKILLS_TAXONOMY = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust",
    "kotlin", "swift", "typescript", "php", "scala", "r", "matlab",
    # Web Frameworks
    "flask", "django", "fastapi", "spring boot", "express", "react",
    "angular", "vue", "next.js", "node.js", "laravel",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "cassandra", "elasticsearch", "firebase",
    # ML / Data Science
    "machine learning", "deep learning", "nlp", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "keras", "pandas",
    "numpy", "matplotlib", "seaborn", "xgboost", "spacy", "nltk",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "jenkins",
    "github actions", "terraform", "ansible", "linux",
    # Concepts
    "rest api", "graphql", "microservices", "agile", "scrum",
    "git", "ci/cd", "tdd", "oop", "data structures", "algorithms",
    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "time management", "critical thinking"
]

# ── Active Job Descriptions ──────────────────────────────────
JOB_DESCRIPTIONS = [
    {
        "id"             : "JD-001",
        "title"          : "Python Developer",
        "department"     : "Engineering",
        "description"    : (
            "We are looking for an experienced Python developer with strong "
            "knowledge of web frameworks, databases, and machine learning libraries "
            "to build scalable backend systems and REST APIs."
        ),
        "requirements"   : (
            "Must have proficiency in Python and Flask or Django. "
            "Experience with SQL databases (PostgreSQL or MySQL) is mandatory. "
            "Familiarity with machine learning libraries such as scikit-learn "
            "or TensorFlow is a plus. REST API design experience required."
        ),
        "skills_required": ["Python", "Flask", "SQL", "Machine Learning",
                             "REST API", "Git", "PostgreSQL"],
        "experience_min" : 2,
        "experience_max" : 6,
    },
    {
        "id"             : "JD-002",
        "title"          : "Data Scientist",
        "department"     : "Analytics",
        "description"    : (
            "Seeking a data scientist to build predictive models, perform "
            "exploratory data analysis, and communicate insights to stakeholders."
        ),
        "requirements"   : (
            "Strong Python skills required. Must know pandas, numpy, and "
            "scikit-learn. Experience with deep learning frameworks preferred. "
            "SQL knowledge essential."
        ),
        "skills_required": ["Python", "Machine Learning", "pandas", "numpy",
                             "scikit-learn", "SQL", "Data Visualization"],
        "experience_min" : 1,
        "experience_max" : 5,
    }
]


class ResumeMatcher:
    """
    Core AI engine that:
      1. Parses raw resume text (NLP simulation without spaCy dependency)
      2. Vectorises JD + resume using TF-IDF
      3. Computes cosine similarity
      4. Computes skill overlap
      5. Computes experience match
      6. Returns a weighted composite score 0–100
    """

    def __init__(self, active_job_id: str = "JD-001"):
        self._candidates: list[dict] = []
        self.active_job   = next(
            (j for j in JOB_DESCRIPTIONS if j["id"] == active_job_id),
            JOB_DESCRIPTIONS[0]
        )

    # ─── Public API ──────────────────────────────────────────

    def compute_match_score(
        self,
        candidate_name  : str,
        candidate_skills: list[str],
        experience_years: float,
        resume_text     : str = ""
    ) -> dict:
        """
        Compute a composite 0-100 match score for one candidate.
        """
        jd_text     = (self.active_job["description"] + " "
                       + self.active_job["requirements"])
        jd_skills   = self.active_job["skills_required"]
        min_exp     = self.active_job["experience_min"]

        # Component 1 — TF-IDF cosine similarity (weight 45 %)
        tfidf_score = self._tfidf_cosine(jd_text, resume_text) if resume_text else 0.40

        # Component 2 — Skill overlap (weight 40 %)
        c_skills_lower = [s.lower() for s in candidate_skills]
        jd_skills_lower= [s.lower() for s in jd_skills]
        matched_skills = [s for s in jd_skills_lower if s in c_skills_lower]
        missing_skills = [s for s in jd_skills_lower if s not in c_skills_lower]
        skill_overlap  = len(matched_skills) / len(jd_skills_lower) if jd_skills_lower else 0

        # Component 3 — Experience match (weight 15 %)
        exp_score = self._experience_score(experience_years, min_exp)

        # Weighted final score
        final = (tfidf_score * 0.45 + skill_overlap * 0.40 + exp_score * 0.15) * 100
        final = round(min(final, 100), 2)

        # Determine status
        if final >= 65:
            status = "shortlisted"
        elif final >= 40:
            status = "under_review"
        else:
            status = "rejected"

        result = {
            "candidate_name"   : candidate_name,
            "match_score"      : final,
            "skill_overlap"    : round(skill_overlap, 3),
            "tfidf_similarity" : round(tfidf_score, 3),
            "experience_score" : round(exp_score, 3),
            "matched_skills"   : [s.title() for s in matched_skills],
            "missing_skills"   : [s.title() for s in missing_skills],
            "experience_years" : experience_years,
            "status"           : status,
            "job_matched"      : self.active_job["title"],
        }

        self._candidates.append(result)
        return result

    def parse_resume_text(self, resume_text: str) -> dict:
        """
        Lightweight NLP parser — extracts structured fields from raw text.
        Production version would use spaCy en_core_web_lg.
        """
        text = resume_text

        # Email extraction
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, text)

        # Phone extraction
        phone_pattern = r'(\+?\d[\d\s\-().]{7,}\d)'
        phones = re.findall(phone_pattern, text)

        # Skills extraction — match against taxonomy
        text_lower  = text.lower()
        found_skills = [s.title() for s in SKILLS_TAXONOMY if s in text_lower]

        # Experience extraction (e.g. "3 years", "2+ years")
        exp_pattern = r'(\d+\.?\d*)\s*\+?\s*years?'
        exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
        max_exp     = max([float(e) for e in exp_matches], default=0)

        # Education extraction (simple keyword approach)
        education_keywords = {
            "phd"      : "Ph.D",
            "m.tech"   : "M.Tech",
            "m.sc"     : "M.Sc",
            "mca"      : "MCA",
            "mba"      : "MBA",
            "b.tech"   : "B.Tech",
            "b.sc"     : "B.Sc",
            "bca"      : "BCA",
            "bachelor" : "Bachelor's",
            "master"   : "Master's",
        }
        found_edu = []
        for kw, label in education_keywords.items():
            if kw in text_lower:
                found_edu.append(label)

        # Name extraction — first non-blank line heuristic
        lines      = [l.strip() for l in text.split('\n') if l.strip()]
        first_line = lines[0] if lines else "Unknown"
        name       = first_line if len(first_line.split()) <= 4 else "Unknown"

        return {
            "name"             : name,
            "email"            : emails[0] if emails else None,
            "phone"            : phones[0].strip() if phones else None,
            "extracted_skills" : found_skills,
            "experience_years" : max_exp,
            "education"        : found_edu,
            "raw_word_count"   : len(text.split()),
        }

    def shortlist(self, threshold: float = 65.0) -> list[dict]:
        """Return all candidates above the threshold, sorted by score."""
        shortlisted = [c for c in self._candidates
                       if c.get("match_score", 0) >= threshold]
        return sorted(shortlisted, key=lambda x: x["match_score"], reverse=True)

    def get_all_candidates(self) -> list[dict]:
        return self._candidates.copy()

    def get_job_descriptions(self) -> list[dict]:
        return JOB_DESCRIPTIONS

    # ─── Private Helpers ──────────────────────────────────────

    def _tfidf_cosine(self, doc1: str, doc2: str) -> float:
        """
        Compute TF-IDF weighted cosine similarity between two documents.
        Pure-Python implementation (no sklearn dependency needed to run demo).
        Production version: sklearn.feature_extraction.text.TfidfVectorizer
        """
        def tokenise(text):
            return re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b', text.lower())

        STOP = {
            "a","an","the","and","or","but","in","on","at","to","for",
            "of","with","is","are","was","were","be","been","have","has",
            "had","do","does","did","will","would","could","should","may",
            "might","shall","this","that","these","those","it","its","we",
            "our","you","your","they","their","he","she","his","her"
        }

        tokens1 = [t for t in tokenise(doc1) if t not in STOP and len(t) > 2]
        tokens2 = [t for t in tokenise(doc2) if t not in STOP and len(t) > 2]

        vocab = list(set(tokens1 + tokens2))
        if not vocab:
            return 0.0

        def tf(tokens):
            counts = Counter(tokens)
            total  = len(tokens) or 1
            return {w: counts[w] / total for w in vocab}

        def idf(w, docs):
            df = sum(1 for d in docs if w in set(d))
            return math.log((len(docs) + 1) / (df + 1)) + 1

        docs = [tokens1, tokens2]
        idf_vals = {w: idf(w, docs) for w in vocab}

        def tfidf_vec(tf_dict):
            return [tf_dict.get(w, 0) * idf_vals[w] for w in vocab]

        vec1 = tfidf_vec(tf(tokens1))
        vec2 = tfidf_vec(tf(tokens2))

        dot  = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a ** 2 for a in vec1))
        mag2 = math.sqrt(sum(b ** 2 for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0
        return round(dot / (mag1 * mag2), 4)

    def _experience_score(self, years: float, min_required: float) -> float:
        """
        Score candidate's experience against the minimum requirement.
            Exact match or above → 1.0
            Within 1 year below  → 0.6
            Within 2 years below → 0.3
            More than 2 below    → 0.1
        """
        gap = years - min_required
        if gap >= 0:
            return 1.0
        elif gap >= -1:
            return 0.6
        elif gap >= -2:
            return 0.3
        return 0.1
