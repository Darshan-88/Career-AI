from backend.app.ai.job_analyzer import extract_skills


# ---------------------------------------------------------
# Skill synonyms
# ---------------------------------------------------------
SKILL_SYNONYMS = {
    "js": "javascript",
    "javascript": "javascript",

    "ts": "typescript",
    "typescript": "typescript",

    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    "mongo": "mongodb",
    "mongodb": "mongodb",

    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "mysql",
    "sql": "sql",

    "rest": "rest api",
    "restful api": "rest api",
    "rest api": "rest api",

    "ml": "machine learning",
    "machine learning": "machine learning",

    "powerbi": "power bi",
    "power bi": "power bi",

    "problem-solving": "problem solving",
    "problem solving": "problem solving",

    "object oriented programming": "oop",
    "object-oriented programming": "oop",
    "oop": "oop",

    "data structures": "dsa",
    "data structures and algorithms": "dsa",
    "dsa": "dsa",
}


# ---------------------------------------------------------
# Normalize skill names
# ---------------------------------------------------------
def normalize_skill(skill: str) -> str:
    skill = skill.lower().strip()

    return SKILL_SYNONYMS.get(skill, skill)


# ---------------------------------------------------------
# Normalize a complete skill list
# ---------------------------------------------------------
def normalize_skills(skills: list[str]) -> list[str]:
    normalized = []

    for skill in skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill not in normalized:
            normalized.append(normalized_skill)

    return normalized


# ---------------------------------------------------------
# Extract skills from a job
# ---------------------------------------------------------
def extract_job_skills(job) -> list[str]:
    """
    Extract skills from the job title, description and
    explicitly stored skills.
    """

    title = getattr(job, "title", "") or ""
    description = getattr(job, "description", "") or ""
    skills_text = getattr(job, "skills", "") or ""

    combined_text = (
        f"{title} "
        f"{description} "
        f"{skills_text}"
    )

    extracted = extract_skills(combined_text)

    return normalize_skills(extracted)


# ---------------------------------------------------------
# Calculate match percentage
# ---------------------------------------------------------
def calculate_match_score(
    resume_skills: list[str],
    job_skills: list[str]
) -> dict:

    resume_skills = normalize_skills(resume_skills)
    job_skills = normalize_skills(job_skills)

    # -----------------------------------------------------
    # If the job has no recognizable skills
    # -----------------------------------------------------
    if not job_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "reason": "No recognizable skills found for this job."
        }

    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched_skills = sorted(
        resume_set.intersection(job_set)
    )

    missing_skills = sorted(
        job_set.difference(resume_set)
    )

    score = round(
        (len(matched_skills) / len(job_set)) * 100
    )

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "reason": "Match calculated successfully."
    }


# ---------------------------------------------------------
# Match one resume against multiple jobs
# ---------------------------------------------------------
def match_resume_to_jobs(
    resume_skills: list[str],
    jobs: list
) -> list[dict]:

    results = []

    normalized_resume_skills = normalize_skills(
        resume_skills
    )

    for job in jobs:

        job_skills = extract_job_skills(job)

        match = calculate_match_score(
            normalized_resume_skills,
            job_skills
        )

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary": job.salary,
            "match_score": match["score"],
            "matched_skills": match["matched_skills"],
            "missing_skills": match["missing_skills"],
            "job_skills": job_skills,
            "reason": match["reason"]
        })

    # -----------------------------------------------------
    # Highest matching jobs first
    # -----------------------------------------------------
    results.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return results


# ---------------------------------------------------------
# Get only the top matching jobs
# ---------------------------------------------------------
def get_top_matches(
    resume_skills: list[str],
    jobs: list,
    limit: int = 10
) -> list[dict]:

    results = match_resume_to_jobs(
        resume_skills,
        jobs
    )

    return results[:limit]