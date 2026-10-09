def generate_questions(role: str, skills: list[str]) -> list[str]:
    questions = [
        f"Tell me about yourself and why you want to work as a {role}.",
        f"Explain one project that demonstrates your ability as a {role}.",
        "Describe a difficult technical problem you solved.",
        "How do you debug a problem when you do not know the root cause?",
        "How do you keep your technical skills up to date?",
    ]

    for skill in skills[:5]:
        questions.append(f"What is {skill} and how have you used it in a project?")

    return questions
