import re


KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "node.js",
    "fastapi",
    "django",
    "flask",
    "sql",
    "mysql",
    "mongodb",
    "firebase",
    "git",
    "github",
    "docker",
    "aws",
    "machine learning",
    "data science",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "power bi",
    "excel",
    "communication",
    "problem solving",
    "dsa",
    "oop",
    "rest api",
]


def extract_skills(text: str) -> list[str]:
    """
    Extract known technical and professional skills from text.
    """

    if not text:
        return []

    text_lower = text.lower()

    found = []

    for skill in KNOWN_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text_lower):
            found.append(skill)

    return sorted(set(found))


def calculate_match_score(
    resume_skills: list[str],
    job_skills: list[str]
) -> int:
    """
    Calculate how closely the resume skills match the job skills.
    """

    if not job_skills:
        return 0

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    job_set = {
        skill.strip().lower()
        for skill in job_skills
    }

    matched_skills = resume_set.intersection(job_set)

    score = (len(matched_skills) / len(job_set)) * 100

    return round(score)


def analyze_job_match(
    resume_text: str,
    job_text: str
) -> dict:
    """
    Compare resume skills against job skills.
    """

    resume_skills = extract_skills(resume_text)

    job_skills = extract_skills(job_text)

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched_skills = sorted(
        resume_set.intersection(job_set)
    )

    missing_skills = sorted(
        job_set - resume_set
    )

    match_score = calculate_match_score(
        resume_skills,
        job_skills
    )

    recommendations = []

    for skill in missing_skills:
        recommendations.append(
            f"Consider learning or improving {skill}."
        )

    if not recommendations:
        recommendations.append(
            "Your skills match the job requirements well."
        )

    return {
        "match_score": match_score,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
    }