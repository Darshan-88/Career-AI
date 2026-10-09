def optimize_resume(resume_text: str, missing_skills: list[str]) -> list[str]:
    suggestions = [
        "Use measurable achievements instead of only listing responsibilities.",
        "Put the most relevant technical skills near the top of the resume.",
        "Use clear project bullets with action verbs.",
    ]

    if missing_skills:
        suggestions.append(
            "If you genuinely have experience with them, add evidence for: "
            + ", ".join(missing_skills[:5])
        )

    return suggestions
