
"use strict";

const CAREERAI_API = "https://career-ai-7m8h.onrender.com";

function getCareerToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        localStorage.getItem("jwt")
    );
}

function escapeCareerHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function setCareerStatus(message, type = "") {
    const status = document.getElementById("careerStatus");
    if (!status) return;

    status.textContent = message;
    status.className = "status show" + (type ? " " + type : "");
}

async function verifyCareerLogin() {
    const token = getCareerToken();

    if (!token) {
        window.location.replace("login.html");
        return false;
    }

    try {
        const response = await fetch(`${CAREERAI_API}/api/users/me`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                Accept: "application/json"
            }
        });

        if (!response.ok) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("token");
            localStorage.removeItem("jwt");
            window.location.replace("login.html");
            return false;
        }

        return true;
    } catch (error) {
        console.error("CareerAI authentication error:", error);
        setCareerStatus(
            "Unable to connect to the backend. Start the FastAPI server and refresh.",
            "error"
        );
        return false;
    }
}

function buildCareerPlan(role, skills, level, hours) {
    const normalizedSkills = skills.map(skill => skill.toLowerCase());
    const priorities = [];

    const hasSkill = (...terms) =>
        normalizedSkills.some(skill =>
            terms.some(term => skill.includes(term))
        );

    if (!hasSkill("python")) {
        priorities.push(
            "Python fundamentals, functions, collections and problem solving"
        );
    }

    if (!hasSkill("sql", "mysql", "postgres", "database")) {
        priorities.push(
            "SQL, joins, aggregation and relational database fundamentals"
        );
    }

    if (/backend|python developer|api developer/i.test(role) &&
        !hasSkill("fastapi", "django", "flask")) {
        priorities.push(
            "Learn a Python backend framework such as FastAPI or Django"
        );
    }

    if (!hasSkill("git", "github")) {
        priorities.push(
            "Git, GitHub, version control and meaningful commit messages"
        );
    }

    if (/data|analyst|scientist/i.test(role) &&
        !hasSkill("pandas")) {
        priorities.push(
            "Pandas, data cleaning and exploratory data analysis"
        );
    }

    if (!hasSkill("testing", "pytest", "unit test")) {
        priorities.push(
            "Automated testing, error handling and debugging"
        );
    }

    if (priorities.length === 0) {
        priorities.push(
            "Practise advanced concepts relevant to your target role"
        );
        priorities.push(
            "Improve testing, deployment and code quality"
        );
        priorities.push(
            "Practise technical interviews and explain your projects clearly"
        );
    }

    const weeks = [
        {
            title: "Week 1 — Build your foundation",
            tasks: [
                "Revise the most important concepts for your target role.",
                "Practise coding or domain-specific problems.",
                "Write down your weakest topics."
            ]
        },
        {
            title: "Week 2 — Develop practical skills",
            tasks: [
                "Build one useful feature.",
                "Connect it to a database or API where appropriate.",
                "Add validation and error handling."
            ]
        },
        {
            title: "Week 3 — Complete a portfolio project",
            tasks: [
                "Finish an end-to-end project.",
                "Upload clean code to GitHub.",
                "Write a README explaining setup and features."
            ]
        },
        {
            title: "Week 4 — Prepare for interviews",
            tasks: [
                "Practise role-specific technical questions.",
                "Explain your projects and decisions aloud.",
                "Update your resume and apply for suitable roles."
            ]
        }
    ];

    return { role, skills, level, hours, priorities, weeks };
}

function renderCareerPlan(plan) {
    const summary = document.getElementById("planSummary");
    const skillList = document.getElementById("skillList");
    const roadmap = document.getElementById("roadmap");
    const projectSuggestion = document.getElementById("projectSuggestion");
    const results = document.getElementById("careerResults");

    summary.textContent =
        `Target role: ${plan.role} | Current level: ${plan.level} | ` +
        `Study commitment: ${plan.hours} hours per week`;

    skillList.replaceChildren();

    plan.priorities.forEach(priority => {
        const item = document.createElement("li");
        item.textContent = priority;
        skillList.appendChild(item);
    });

    roadmap.replaceChildren();

    plan.weeks.forEach(week => {
        const card = document.createElement("article");
        card.className = "plan-card";

        const heading = document.createElement("h3");
        heading.textContent = week.title;
        card.appendChild(heading);

        const list = document.createElement("ul");

        week.tasks.forEach(task => {
            const item = document.createElement("li");
            item.textContent = task;
            list.appendChild(item);
        });

        card.appendChild(list);
        roadmap.appendChild(card);
    });

    projectSuggestion.replaceChildren();

    const projectTitle = document.createElement("h3");
    projectTitle.textContent = `${plan.role} Portfolio Project`;

    const projectDescription = document.createElement("p");
    projectDescription.textContent =
        "Build a practical application relevant to your target role. " +
        "Include input validation, database operations, authentication " +
        "where appropriate, tests, clear documentation and screenshots.";

    const projectSkills = document.createElement("p");
    projectSkills.textContent =
        `Skills to demonstrate: ${plan.skills.join(", ")}`;

    projectSuggestion.append(
        projectTitle,
        projectDescription,
        projectSkills
    );

    results.hidden = false;
}

function initializeCareerPage() {
    const form = document.getElementById("careerForm");
    const button = document.getElementById("generateButton");

    if (!form || !button) return;

    verifyCareerLogin();

    form.addEventListener("submit", async event => {
        event.preventDefault();
        button.disabled = true;
        setCareerStatus("Preparing your career roadmap…");

        try {
            const role =
                document.getElementById("targetRole").value.trim();

            const skills = document.getElementById("skills").value
                .split(/[,\n]/)
                .map(skill => skill.trim())
                .filter(Boolean);

            const level =
                document.getElementById("experience").value;

            const hours =
                document.getElementById("hours").value;

            if (!role || skills.length === 0) {
                setCareerStatus(
                    "Enter your target role and at least one skill.",
                    "error"
                );
                return;
            }

            const plan = buildCareerPlan(role, skills, level, hours);
            renderCareerPlan(plan);

            setCareerStatus(
                "Your career roadmap is ready. Follow it week by week.",
                "success"
            );

            document.getElementById("careerResults").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        } catch (error) {
            console.error("Career plan generation failed:", error);
            setCareerStatus(
                "Unable to prepare the career plan. Please try again.",
                "error"
            );
        } finally {
            button.disabled = false;
        }
    });
}

document.addEventListener("DOMContentLoaded", initializeCareerPage);
