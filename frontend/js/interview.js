
"use strict";

const CAREERAI_INTERVIEW_API = "http://127.0.0.1:8000";

function getInterviewToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        localStorage.getItem("jwt")
    );
}

function setInterviewStatus(message, type = "") {
    const status = document.getElementById("interviewStatus");
    if (!status) return;

    status.textContent = message;
    status.className = "status show" + (type ? " " + type : "");
}

async function verifyInterviewLogin() {
    const token = getInterviewToken();

    if (!token) {
        window.location.replace("login.html");
        return false;
    }

    try {
        const response = await fetch(
            `${CAREERAI_INTERVIEW_API}/api/users/me`,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    Accept: "application/json"
                }
            }
        );

        if (!response.ok) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("token");
            localStorage.removeItem("jwt");
            window.location.replace("login.html");
            return false;
        }

        return true;
    } catch (error) {
        console.error("Interview authentication error:", error);
        setInterviewStatus(
            "Unable to connect to the backend. Start FastAPI and refresh.",
            "error"
        );
        return false;
    }
}

function renderInterviewQuestions(questions) {
    const questionList = document.getElementById("questionList");
    questionList.replaceChildren();

    if (!questions.length) {
        const message = document.createElement("p");
        message.textContent =
            "No questions were returned. Try another role or skill set.";
        questionList.appendChild(message);
        return;
    }

    questions.forEach((item, index) => {
        const questionText = typeof item === "string"
            ? item
            : (item.question || item.text || JSON.stringify(item));

        const card = document.createElement("article");
        card.className = "question-card";

        const heading = document.createElement("h3");
        heading.textContent = `Question ${index + 1}`;

        const question = document.createElement("p");
        question.textContent = questionText;

        const label = document.createElement("label");
        const answerId = `interview-answer-${index}`;
        label.htmlFor = answerId;
        label.textContent = "Your practice answer";

        const answer = document.createElement("textarea");
        answer.id = answerId;
        answer.className = "answer-area";
        answer.rows = 4;
        answer.placeholder =
            "Write your answer here. Include an example from your project or internship.";

        const actions = document.createElement("div");
        actions.className = "question-actions";

        const copyButton = document.createElement("button");
        copyButton.type = "button";
        copyButton.className = "secondary-btn";
        copyButton.textContent = "Copy My Answer";
        copyButton.dataset.copyAnswer = answerId;

        actions.appendChild(copyButton);
        card.append(heading, question, label, answer, actions);
        questionList.appendChild(card);
    });
}

function initializeInterviewPage() {
    const form = document.getElementById("interviewForm");
    const button = document.getElementById("generateButton");
    const questionList = document.getElementById("questionList");
    const printButton = document.getElementById("printButton");

    if (!form || !button || !questionList || !printButton) return;

    verifyInterviewLogin();

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const role = document.getElementById("role").value.trim();
        const skills = document.getElementById("skills").value
            .split(/[,\n]/)
            .map(skill => skill.trim())
            .filter(Boolean);

        if (!role || skills.length === 0) {
            setInterviewStatus(
                "Enter a target role and at least one skill.",
                "error"
            );
            return;
        }

        button.disabled = true;
        setInterviewStatus("Generating interview questions…");

        try {
            const token = getInterviewToken();

            const response = await fetch(
                `${CAREERAI_INTERVIEW_API}/api/interviews/generate`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                        Accept: "application/json"
                    },
                    body: JSON.stringify({ role, skills })
                }
            );

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    data.detail || `Request failed (${response.status})`
                );
            }

            const questions = Array.isArray(data.questions)
                ? data.questions
                : [];

            renderInterviewQuestions(questions);

            document.getElementById("interviewResults").hidden = false;

            setInterviewStatus(
                `Generated ${questions.length} question(s) for ${role}.`,
                "success"
            );

            document.getElementById("interviewResults").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        } catch (error) {
            console.error("Question generation failed:", error);
            setInterviewStatus(
                error.message ||
                "Unable to generate questions. Please try again.",
                "error"
            );
        } finally {
            button.disabled = false;
        }
    });

    questionList.addEventListener("click", async event => {
        const copyButton = event.target.closest("[data-copy-answer]");
        if (!copyButton) return;

        const answer = document.getElementById(
            copyButton.dataset.copyAnswer
        );

        if (!answer || !answer.value.trim()) {
            setInterviewStatus(
                "Write your answer before copying it.",
                "error"
            );
            return;
        }

        try {
            await navigator.clipboard.writeText(answer.value);
            setInterviewStatus("Your answer was copied.", "success");
        } catch (error) {
            console.error("Clipboard error:", error);
            setInterviewStatus(
                "Clipboard access failed. Select and copy the answer manually.",
                "error"
            );
        }
    });

    printButton.addEventListener("click", () => window.print());
}

document.addEventListener("DOMContentLoaded", initializeInterviewPage);
