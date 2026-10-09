/* =========================================================
   CAREERAI - JOB MATCH INTELLIGENCE
   Resume + External Job Description Analysis
========================================================= */

const API_BASE_URL = "https://career-ai-7m8h.onrender.com";

/* =========================================================
   AUTH TOKEN
========================================================= */

function getAuthToken() {
    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        localStorage.getItem("jwt")
    );
}

/* =========================================================
   ELEMENTS
========================================================= */

const resumeFileInput =
    document.getElementById("resumeFile");

const jobDescriptionFileInput =
    document.getElementById("jobDescriptionFile");

const resumeFileName =
    document.getElementById("resumeFileName");

const jobDescriptionFileName =
    document.getElementById("jobDescriptionFileName");

const analyzeButton =
    document.getElementById("analyzeButton");

const statusMessage =
    document.getElementById("statusMessage");

const resultSection =
    document.getElementById("resultSection");


/* =========================================================
   FILE NAME DISPLAY
========================================================= */

if (resumeFileInput) {

    resumeFileInput.addEventListener("change", function () {

        const file = resumeFileInput.files[0];

        if (!file) {
            return;
        }

        if (resumeFileName) {
            resumeFileName.textContent = file.name;
        }

    });

}


if (jobDescriptionFileInput) {

    jobDescriptionFileInput.addEventListener(
        "change",
        function () {

            const file =
                jobDescriptionFileInput.files[0];

            if (!file) {
                return;
            }

            if (jobDescriptionFileName) {
                jobDescriptionFileName.textContent =
                    file.name;
            }

        }
    );

}


/* =========================================================
   ANALYZE JOB MATCH
========================================================= */

if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        analyzeJobMatch
    );

}


/* =========================================================
   MAIN ANALYSIS FUNCTION
========================================================= */

async function analyzeJobMatch() {

    /* -----------------------------------------
       CHECK FILES
    ----------------------------------------- */

    const resumeFile =
        resumeFileInput?.files?.[0];

    const jobDescriptionFile =
        jobDescriptionFileInput?.files?.[0];


    if (!resumeFile) {

        showStatus(
            "Please upload your resume first.",
            "error"
        );

        return;
    }


    if (!jobDescriptionFile) {

        showStatus(
            "Please upload a job description first.",
            "error"
        );

        return;
    }


    /* -----------------------------------------
       CHECK AUTHENTICATION
    ----------------------------------------- */

    const token = getAuthToken();

    if (!token) {

        showStatus(
            "Your session has expired. Please login again.",
            "error"
        );

        return;
    }


    /* -----------------------------------------
       VALIDATE FILE TYPES
    ----------------------------------------- */

    const allowedExtensions = [
        ".pdf",
        ".docx",
        ".txt"
    ];


    const resumeValid =
        allowedExtensions.some(
            extension =>
                resumeFile.name
                    .toLowerCase()
                    .endsWith(extension)
        );


    const jobDescriptionValid =
        allowedExtensions.some(
            extension =>
                jobDescriptionFile.name
                    .toLowerCase()
                    .endsWith(extension)
        );


    if (!resumeValid) {

        showStatus(
            "Resume must be a PDF, DOCX or TXT file.",
            "error"
        );

        return;
    }


    if (!jobDescriptionValid) {

        showStatus(
            "Job description must be a PDF, DOCX or TXT file.",
            "error"
        );

        return;
    }


    /* -----------------------------------------
       LOADING STATE
    ----------------------------------------- */

    analyzeButton.disabled = true;

    analyzeButton.textContent =
        "Analyzing Job Match...";


    showStatus(
        "CareerAI is comparing your resume with the job description...",
        "loading"
    );


    /* -----------------------------------------
       CREATE FORM DATA
    ----------------------------------------- */

    const formData = new FormData();

    formData.append(
        "resume_file",
        resumeFile
    );

    formData.append(
        "job_description_file",
        jobDescriptionFile
    );


    /* =====================================================
       API REQUEST

       IMPORTANT:
       THIS IS THE CORRECT BACKEND ENDPOINT.
    ===================================================== */

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/analysis/external-job-match`,
            {
                method: "POST",

                headers: {
                    Authorization: `Bearer ${token}`
                },

                body: formData
            }
        );


        /* -----------------------------------------
           READ RESPONSE
        ----------------------------------------- */

        const data =
            await response.json();


        /* -----------------------------------------
           HANDLE ERROR
        ----------------------------------------- */

        if (!response.ok) {

            let errorMessage =
                "Job match analysis failed.";


            if (data.detail) {

                if (
                    typeof data.detail === "string"
                ) {

                    errorMessage =
                        data.detail;

                } else {

                    errorMessage =
                        "Unable to analyze the job description.";

                }

            }


            throw new Error(errorMessage);
        }


        /* -----------------------------------------
           DISPLAY RESULT
        ----------------------------------------- */

        displayJobMatchResult(data);


        showStatus(
            "Job match analysis completed successfully.",
            "success"
        );

    }


    catch (error) {

        console.error(
            "Job match analysis error:",
            error
        );


        showStatus(
            error.message ||
            "Something went wrong while analyzing the job.",
            "error"
        );

    }


    finally {

        analyzeButton.disabled = false;

        analyzeButton.textContent =
            "✨ Analyze Job Match →";

    }

}


/* =========================================================
   DISPLAY RESULT
========================================================= */

function displayJobMatchResult(data) {

    if (!resultSection) {
        return;
    }


    /* -----------------------------------------
       MATCH SCORE
    ----------------------------------------- */

    const score =
        Number(data.match_score || 0);


    const scoreElement =
        document.getElementById("matchScore");


    if (scoreElement) {

        scoreElement.textContent =
            `${score}%`;

    }


    /* -----------------------------------------
       RESUME SKILLS
    ----------------------------------------- */

    renderSkills(
        "resumeSkills",
        data.resume_skills || []
    );


    /* -----------------------------------------
       JOB SKILLS
    ----------------------------------------- */

    renderSkills(
        "jobSkills",
        data.job_skills || []
    );


    /* -----------------------------------------
       MATCHED SKILLS
    ----------------------------------------- */

    renderSkills(
        "matchedSkills",
        data.matched_skills || []
    );


    /* -----------------------------------------
       MISSING SKILLS
    ----------------------------------------- */

    renderSkills(
        "missingSkills",
        data.missing_skills || []
    );


    /* -----------------------------------------
       RECOMMENDATIONS
    ----------------------------------------- */

    const recommendationList =
        document.getElementById(
            "recommendationList"
        );


    if (recommendationList) {

        recommendationList.innerHTML = "";


        const recommendations =
            data.recommendations || [];


        if (recommendations.length === 0) {

            const li =
                document.createElement("li");

            li.textContent =
                "Your profile matches this job well.";

            recommendationList.appendChild(li);

        } else {

            recommendations.forEach(
                recommendation => {

                    const li =
                        document.createElement("li");

                    li.textContent =
                        recommendation;

                    recommendationList.appendChild(li);

                }
            );

        }

    }


    /* -----------------------------------------
       SHOW RESULT
    ----------------------------------------- */

    resultSection.classList.remove(
        "hidden"
    );


    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================================
   RENDER SKILLS
========================================================= */

function renderSkills(
    elementId,
    skills
) {

    const container =
        document.getElementById(
            elementId
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !skills ||
        skills.length === 0
    ) {

        const empty =
            document.createElement("span");

        empty.className =
            "text-muted";

        empty.textContent =
            "None identified";

        container.appendChild(empty);

        return;
    }


    skills.forEach(skill => {

        const tag =
            document.createElement("span");

        tag.className =
            "skill-tag";

        tag.textContent =
            skill;

        container.appendChild(tag);

    });

}


/* =========================================================
   STATUS MESSAGE
========================================================= */

function showStatus(
    message,
    type
) {

    if (!statusMessage) {
        return;
    }


    statusMessage.textContent =
        message;


    statusMessage.className =
        "job-match-status";


    if (type === "success") {

        statusMessage.classList.add(
            "success"
        );

    }


    else if (type === "error") {

        statusMessage.classList.add(
            "error"
        );

    }


    else {

        statusMessage.classList.add(
            "loading"
        );

    }

}