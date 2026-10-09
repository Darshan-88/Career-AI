def calculate_skill_gap(current: list[str], required: list[str]) -> dict:
    current_set = {x.strip().lower() for x in current if x.strip()}
    required_set = {x.strip().lower() for x in required if x.strip()}

    matched = sorted(current_set & required_set)
    missing = sorted(required_set - current_set)

    score = round((len(matched) / len(required_set)) * 100) if required_set else 0

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }
