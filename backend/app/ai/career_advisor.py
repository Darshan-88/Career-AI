def career_advice(skills: list[str], target_role: str) -> list[str]:
    advice = []

    if "python" not in skills:
        advice.append("Strengthen Python fundamentals and build one practical project.")

    if target_role.lower() in {"data scientist", "data analyst"}:
        if "sql" not in skills:
            advice.append("Learn SQL and practice joins, aggregation and window functions.")
        if "pandas" not in skills:
            advice.append("Learn Pandas for data cleaning and analysis.")
        if "power bi" not in skills:
            advice.append("Learn Power BI or another visualization tool.")

    if target_role.lower() in {"backend developer", "python developer"}:
        if "fastapi" not in skills and "django" not in skills:
            advice.append("Learn a Python backend framework such as FastAPI or Django.")
        if "sql" not in skills:
            advice.append("Strengthen SQL and relational database fundamentals.")

    if not advice:
        advice.append("Build two portfolio projects and practice role-specific interview questions.")

    return advice
