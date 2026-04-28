# ============================================================
#  AI Resume Screening System — data_generator.py
#  Generates synthetic candidate resume datasets for testing
#
#  Usage:
#    python data_generator.py                  → generates 20 candidates
#    python data_generator.py --count 50       → generates 50 candidates
#    python data_generator.py --output custom.json
#
#  Output: sample_data/candidates.json
#          sample_data/job_descriptions.json
# ============================================================

import json
import random
import argparse
import os
from datetime import datetime

# ─── Seed data pools ─────────────────────────────────────────

FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Arjun", "Meera", "Kiran",
    "Divya", "Rohan", "Nisha", "Vijay", "Pooja", "Suresh", "Ananya",
    "Manish", "Kavya", "Deepak", "Ritu", "Sanjay", "Lakshmi",
    "Aditya", "Shruti", "Nikhil", "Swathi", "Rajan", "Anjali"
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Joshi", "Mehta",
    "Nair", "Reddy", "Rao", "Iyer", "Pillai", "Das", "Banerjee",
    "Mishra", "Tiwari", "Verma", "Shah", "Bhat", "Chopra"
]

SKILL_POOLS = {
    "core_python": ["Python", "Flask", "Django", "FastAPI"],
    "databases"  : ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
    "ml_ds"      : ["Machine Learning", "scikit-learn", "pandas", "numpy",
                    "TensorFlow", "PyTorch", "NLP", "Deep Learning"],
    "web"        : ["REST API", "GraphQL", "HTML", "CSS", "JavaScript", "React"],
    "devops"     : ["Docker", "Git", "AWS", "Linux", "CI/CD", "Kubernetes"],
    "soft"       : ["Communication", "Teamwork", "Problem Solving", "Leadership"]
}

EDUCATION_OPTIONS = [
    "B.Tech Computer Science, IIT Delhi",
    "MCA, Chandigarh University",
    "B.Sc Computer Science, Delhi University",
    "M.Tech Data Science, NIT Trichy",
    "BCA, Pune University",
    "M.Sc IT, Manipal University",
    "B.Tech IT, VIT Vellore",
    "MBA Information Technology, BITS Pilani",
    "MCA, Osmania University",
    "B.Tech CSE, JNTU Hyderabad"
]

COMPANIES = [
    "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
    "Accenture India", "Cognizant", "Capgemini", "IBM India", "Oracle India",
    "Amazon India", "Microsoft India", "Google India", "Flipkart", "Swiggy"
]

RESUME_TEMPLATES = [
    (
        "{name} is a {exp}-year experienced software developer specialising in Python "
        "and web development. Has worked extensively with {skill1} and {skill2} to "
        "build production-grade applications. Currently at {company}, responsible for "
        "designing RESTful APIs and maintaining database schemas. Passionate about "
        "clean code and agile development practices."
    ),
    (
        "Motivated {exp}-year Python engineer with a strong background in {skill1}, "
        "{skill2}, and data-driven application development. At {company}, led a team "
        "of three developers in migrating legacy monolith to microservices. Experienced "
        "in machine learning pipeline development using scikit-learn and pandas."
    ),
    (
        "{name} brings {exp} years of hands-on experience in full-stack Python development. "
        "Core strengths include {skill1}, {skill2}, and database management. Has delivered "
        "over 12 production projects at {company}. Holds strong fundamentals in algorithms, "
        "OOP design patterns, and agile/Scrum methodologies."
    ),
    (
        "Detail-oriented software engineer with {exp} years in backend Python development. "
        "Proficient in {skill1} and {skill2}. At {company}, built automated data processing "
        "pipelines handling 1M+ records per day. Strong understanding of cloud deployments "
        "using Docker and AWS. Quick learner with excellent problem-solving skills."
    )
]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email(name):
    parts = name.lower().split()
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{parts[0]}.{parts[1]}{random.randint(10,99)}@{random.choice(domains)}"


def random_phone():
    return f"+91-{random.randint(7000000000, 9999999999)}"


def generate_candidate(index: int) -> dict:
    """Generate one synthetic candidate record."""
    name        = random_name()
    exp         = round(random.uniform(0.5, 8.0), 1)
    education   = random.choice(EDUCATION_OPTIONS)
    company     = random.choice(COMPANIES)

    # Pick a random mix of skills (vary by experience level)
    num_skills = max(2, int(exp * 1.2) + random.randint(0, 3))
    all_skills = (
        random.choices(SKILL_POOLS["core_python"], k=random.randint(1, 3)) +
        random.choices(SKILL_POOLS["databases"],   k=random.randint(1, 2)) +
        random.choices(SKILL_POOLS["ml_ds"],       k=random.randint(0, 2)) +
        random.choices(SKILL_POOLS["devops"],      k=random.randint(0, 2)) +
        random.choices(SKILL_POOLS["soft"],        k=1)
    )
    skills = list(dict.fromkeys(all_skills))[:num_skills]   # deduplicate, trim

    # Pick two featured skills for resume text
    skill1 = skills[0] if skills else "Python"
    skill2 = skills[1] if len(skills) > 1 else "SQL"

    resume_text = random.choice(RESUME_TEMPLATES).format(
        name=name, exp=int(exp), company=company, skill1=skill1, skill2=skill2
    )

    return {
        "id"           : f"CAND-{index:04d}",
        "name"         : name,
        "email"        : random_email(name),
        "phone"        : random_phone(),
        "experience"   : exp,
        "education"    : education,
        "skills"       : skills,
        "current_company": company,
        "resume_text"  : resume_text,
        "generated_at" : datetime.now().isoformat(timespec='seconds')
    }


def generate_dataset(count: int = 20) -> list[dict]:
    """Generate `count` synthetic candidate records."""
    print(f"[data_generator] Generating {count} candidate records...")
    return [generate_candidate(i + 1) for i in range(count)]


def save_candidates(candidates: list[dict], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"count": len(candidates), "candidates": candidates},
                  f, indent=2, ensure_ascii=False)
    print(f"[data_generator] Saved {len(candidates)} candidates → {output_path}")


def save_job_descriptions(output_path: str) -> None:
    """Save job descriptions to a JSON file for reference."""
    # Import here to avoid circular dependency
    from matcher import JOB_DESCRIPTIONS
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"job_descriptions": JOB_DESCRIPTIONS}, f, indent=2)
    print(f"[data_generator] Saved job descriptions → {output_path}")


# ─── CLI Entry Point ─────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic resume dataset for AI Resume Screening System"
    )
    parser.add_argument(
        "--count", type=int, default=20,
        help="Number of candidate records to generate (default: 20)"
    )
    parser.add_argument(
        "--output", type=str, default="sample_data/candidates.json",
        help="Output file path (default: sample_data/candidates.json)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility (optional)"
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"[data_generator] Using random seed: {args.seed}")

    candidates = generate_dataset(args.count)
    save_candidates(candidates, args.output)
    save_job_descriptions("sample_data/job_descriptions.json")

    # Print a preview of the first 3 records
    print("\n── Sample Records Preview ──────────────────────────")
    for c in candidates[:3]:
        print(f"  {c['id']}  {c['name']:<25}  "
              f"{c['experience']}yr  "
              f"Skills: {', '.join(c['skills'][:4])}")
    print(f"  ... and {len(candidates) - 3} more")
    print("────────────────────────────────────────────────────")
    print("Done. Run `python app.py` to start the server.")
