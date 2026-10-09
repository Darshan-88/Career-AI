/* =========================================================
   CAREERAI - RESUME AI
   Resume upload + AI analysis
========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";


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

const resumeForm =
    document.getElementById("resumeForm");

const resumeFile =
    document.getElementById("resumeFile");

const targetRole =
    document.getElementById("targetRole");

const fileNameDisplay =
    document.getElementById("fileNameDisplay");

const fileNameText =
    document.getElementById("fileNameText");

const chooseResumeButton =
    document.getElementById("chooseResumeButton");

const uploadZone =
    document.getElementById("uploadZone");

const analyzeButton =
    document.getElementById("analyzeButton");

const uploadStatus =
    document.getElementById("uploadStatus");

const resultSection =
    document.getElementById("resultSection");


/* =========================================================
   FILE NAME
========================================================= */

function updateFileName(file) {

    if (!fileNameDisplay) {
        return;
    }


    if (fileNameText) {

        fileNameText.textContent =
            file.name;

        return;

    }


    fileNameDisplay.textContent =
        file.name;

}


/* =========================================================
   STATUS
========================================================= */

function showStatus(message, type) {

    if (!uploadStatus) {
        return;
    }


    uploadStatus.textContent =
        message;


    uploadStatus.className =
        "";


    if (type === "success") {

        uploadStatus.classList.add(
            "text-success"
        );

    }

    else if (type === "error") {

        uploadStatus.classList.add(
            "text-danger"
        );

    }

    else {

        uploadStatus.classList.add(
            "text-muted"
        );

    }

}


/* =========================================================
   FILE SELECTION
========================================================= */

if (resumeFile) {

    resumeFile.addEventListener(
        "change",
        function () {

            const file =
                resumeFile.files[0];


            if (!file) {

                if (fileNameText) {

                    fileNameText.textContent =
                        "No file selected";

                }

                return;

            }


            updateFileName(file);


            showStatus(
                "Resume selected. Ready for AI analysis.",
                "success"
            );

        }
    );

}


/* =========================================================
   CHOOSE RESUME BUTTON
========================================================= */

if (
    chooseResumeButton &&
    resumeFile
) {

    chooseResumeButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            event.stopPropagation();

            resumeFile.click();

        }
    );

}


/* =========================================================
   UPLOAD ZONE
========================================================= */

if (
    uploadZone &&
    resumeFile
) {

    uploadZone.addEventListener(
        "click",
        function (event) {

            if (
                event.target !==
                chooseResumeButton
            ) {

                resumeFile.click();

            }

        }
    );


    uploadZone.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            uploadZone.classList.add(
                "dragging"
            );

        }
    );


    uploadZone.addEventListener(
        "dragleave",
        function () {

            uploadZone.classList.remove(
                "dragging"
            );

        }
    );


    uploadZone.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            uploadZone.classList.remove(
                "dragging"
            );


            const files =
                event.dataTransfer.files;


            if (
                files &&
                files.length > 0
            ) {

                updateFileName(
                    files[0]
                );


                showStatus(
                    "Resume selected. Ready for AI analysis.",
                    "success"
                );


                /*
                   DataTransfer allows us to assign
                   the dropped file to the input.
                */

                try {

                    const dataTransfer =
                        new DataTransfer();

                    dataTransfer.items.add(
                        files[0]
                    );

                    resumeFile.files =
                        dataTransfer.files;

                }

                catch (error) {

                    console.error(
                        "Drop handling error:",
                        error
                    );

                }

            }

        }
    );

}


/* =========================================================
   ANALYZE RESUME
========================================================= */

if (resumeForm) {

    resumeForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const file =
                resumeFile?.files?.[0];


            const role =
                targetRole?.value?.trim();


            /* =============================================
               FILE VALIDATION
            ============================================== */

            if (!file) {

                showStatus(
                    "Please select your resume first.",
                    "error"
                );

                return;

            }


            /* =============================================
               ROLE VALIDATION
            ============================================== */

            if (!role) {

                showStatus(
                    "Please select your target role.",
                    "error"
                );

                return;

            }


            /* =============================================
               AUTHENTICATION
            ============================================== */

            const token =
                getAuthToken();


            if (!token) {

                showStatus(
                    "Your session has expired. Please login again.",
                    "error"
                );

                setTimeout(
                    function () {

                        window.location.href =
                            "login.html";

                    },
                    1200
                );

                return;

            }


            /* =============================================
               FILE TYPE
            ============================================== */

            const allowedExtensions = [
                ".pdf",
                ".docx",
                ".txt"
            ];


            const fileName =
                file.name.toLowerCase();


            const validFile =
                allowedExtensions.some(
                    function (extension) {

                        return fileName.endsWith(
                            extension
                        );

                    }
                );


            if (!validFile) {

                showStatus(
                    "Please upload a PDF, DOCX or TXT resume.",
                    "error"
                );

                return;

            }


            /* =============================================
               LOADING
            ============================================== */

            if (analyzeButton) {

                analyzeButton.disabled =
                    true;

                analyzeButton.textContent =
                    "Analyzing Resume...";

            }


            showStatus(
                "CareerAI is analyzing your resume...",
                "loading"
            );


            /* =============================================
               FORM DATA
            ============================================== */

            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            formData.append(
                "target_role",
                role
            );


            /* =============================================
               API REQUEST
            ============================================== */

            try {

                console.log(
                    "Sending resume to CareerAI API..."
                );


                const response =
                    await fetch(
                        `${API_BASE_URL}/api/analysis/upload-and-analyze`,
                        {
                            method: "POST",

                            headers: {
                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body: formData
                        }
                    );


                console.log(
                    "Resume API status:",
                    response.status
                );


                let data;


                try {

                    data =
                        await response.json();

                }

                catch (jsonError) {

                    throw new Error(
                        "The server returned an invalid response."
                    );

                }


                if (!response.ok) {

                    let errorMessage =
                        "Resume analysis failed.";


                    if (data.detail) {

                        errorMessage =
                            typeof data.detail ===
                            "string"

                                ? data.detail

                                : "Unable to analyze resume.";

                    }


                    throw new Error(
                        errorMessage
                    );

                }


                console.log(
                    "Resume analysis result:",
                    data
                );


                displayAnalysisResult(
                    data
                );


                showStatus(
                    "Resume analyzed successfully.",
                    "success"
                );

            }

            catch (error) {

                console.error(
                    "Resume analysis error:",
                    error
                );


                showStatus(
                    error.message ||
                    "Something went wrong while analyzing your resume.",
                    "error"
                );

            }

            finally {

                if (analyzeButton) {

                    analyzeButton.disabled =
                        false;

                    analyzeButton.textContent =
                        "✨ Analyze Resume";

                }

            }

        }
    );

}


/* =========================================================
   DISPLAY RESULT
========================================================= */

function displayAnalysisResult(data) {

    if (!resultSection) {
        return;
    }


    const score =
        Number(
            data.score || 0
        );


    const scoreElement =
        document.getElementById(
            "resumeScore"
        );


    if (scoreElement) {

        scoreElement.textContent =
            `${score}%`;

    }


    const roleElement =
        document.getElementById(
            "resultRole"
        );


    if (roleElement) {

        roleElement.textContent =
            formatRole(
                data.target_role ||
                "Software Engineer"
            );

    }


    const matchedSkills =
        data.matched_skills ||
        [];


    const extractedSkills =
        data.extracted_skills ||
        [];


    const missingSkills =
        data.missing_skills ||
        [];


    renderSkills(
        "matchedSkills",
        matchedSkills,
        "skill-tag"
    );


    renderSkills(
        "extractedSkills",
        extractedSkills,
        "skill-tag"
    );


    renderSkills(
        "missingSkills",
        missingSkills,
        "skill-tag missing"
    );


    const recommendations =
        data.recommendations ||
        [];


    const recommendationList =
        document.getElementById(
            "recommendationList"
        );


    if (recommendationList) {

        recommendationList.innerHTML =
            "";


        if (
            recommendations.length ===
            0
        ) {

            const li =
                document.createElement(
                    "li"
                );


            li.textContent =
                "Your profile is looking strong for this role.";


            recommendationList.appendChild(
                li
            );

        }

        else {

            recommendations.forEach(
                function (recommendation) {

                    const li =
                        document.createElement(
                            "li"
                        );


                    li.textContent =
                        recommendation;


                    recommendationList.appendChild(
                        li
                    );

                }
            );

        }

    }


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
    skills,
    className
) {

    const container =
        document.getElementById(
            elementId
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        "";


    if (
        !skills ||
        skills.length === 0
    ) {

        const empty =
            document.createElement(
                "span"
            );


        empty.className =
            "text-muted";


        empty.textContent =
            "None identified";


        container.appendChild(
            empty
        );


        return;

    }


    skills.forEach(
        function (skill) {

            const tag =
                document.createElement(
                    "span"
                );


            tag.className =
                className;


            tag.textContent =
                skill;


            container.appendChild(
                tag
            );

        }
    );

}


/* =========================================================
   FORMAT ROLE
========================================================= */

function formatRole(role) {

    return role.replace(
        /\b\w/g,
        function (letter) {

            return letter.toUpperCase();

        }
    );

}
/* =========================================================
   EXTERNAL JOB DESCRIPTION MATCHER
========================================================= */

const jdResumeFile =
    document.getElementById("jdResumeFile");

const jobDescriptionFile =
    document.getElementById("jobDescriptionFile");

const jdResumeFileName =
    document.getElementById("jdResumeFileName");

const jobDescriptionFileName =
    document.getElementById("jobDescriptionFileName");

const analyzeJobButton =
    document.getElementById("analyzeJobButton");

const jobMatchStatus =
    document.getElementById("jobMatchStatus");

const jobMatchResult =
    document.getElementById("jobMatchResult");


/* ---------------------------------------------------------
   FILE NAME DISPLAY
--------------------------------------------------------- */

if (jdResumeFile) {

    jdResumeFile.addEventListener(
        "change",
        function () {

            const file =
                jdResumeFile.files[0];

            if (file && jdResumeFileName) {
                jdResumeFileName.textContent =
                    file.name;
            }

        }
    );

}


if (jobDescriptionFile) {

    jobDescriptionFile.addEventListener(
        "change",
        function () {

            const file =
                jobDescriptionFile.files[0];

            if (file && jobDescriptionFileName) {
                jobDescriptionFileName.textContent =
                    file.name;
            }

        }
    );

}


/* ---------------------------------------------------------
   ANALYZE JOB
--------------------------------------------------------- */

if (analyzeJobButton) {

    analyzeJobButton.addEventListener(
        "click",
        async function () {

            const resume =
                jdResumeFile?.files[0];

            const jobDescription =
                jobDescriptionFile?.files[0];


            /* ---------- Validation ---------- */

            if (!resume) {

                showJobMatchStatus(
                    "Please select your resume.",
                    "error"
                );

                return;
            }


            if (!jobDescription) {

                showJobMatchStatus(
                    "Please select a job description.",
                    "error"
                );

                return;
            }


            /* ---------- Authentication ---------- */

            const token =
                getAuthToken();

            if (!token) {

                showJobMatchStatus(
                    "Your session has expired. Please login again.",
                    "error"
                );

                return;
            }


            /* ---------- File validation ---------- */

            const allowedExtensions = [
                ".pdf",
                ".docx",
                ".txt"
            ];


            const resumeName =
                resume.name.toLowerCase();

            const jobName =
                jobDescription.name.toLowerCase();


            const validResume =
                allowedExtensions.some(
                    extension =>
                        resumeName.endsWith(extension)
                );


            const validJob =
                allowedExtensions.some(
                    extension =>
                        jobName.endsWith(extension)
                );


            if (!validResume || !validJob) {

                showJobMatchStatus(
                    "Only PDF, DOCX and TXT files are supported.",
                    "error"
                );

                return;
            }


            /* ---------- Loading ---------- */

            analyzeJobButton.disabled = true;

            analyzeJobButton.textContent =
                "Analyzing Job Match...";

            showJobMatchStatus(
                "CareerAI is comparing your resume with the job description...",
                "loading"
            );


            /* ---------- FormData ---------- */

            const formData =
                new FormData();

            formData.append(
                "resume_file",
                resume
            );

            formData.append(
                "job_description_file",
                jobDescription
            );


            /* ---------- API ---------- */

            try {

                    const response =
    await fetch(
        `${API_BASE_URL}/api/analysis/external-job-match`,
        {
                            method: "POST",

                            headers: {
                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    const message =
                        typeof data.detail === "string"
                            ? data.detail
                            : "Unable to analyze the job description.";

                    throw new Error(message);
                }


                displayJobMatchResult(data);


                showJobMatchStatus(
                    "Job match analysis completed successfully.",
                    "success"
                );


            } catch (error) {

                console.error(
                    "Job match error:",
                    error
                );


                showJobMatchStatus(
                    error.message ||
                    "Something went wrong while analyzing the job.",
                    "error"
                );


            } finally {

                analyzeJobButton.disabled = false;

                analyzeJobButton.textContent =
                    "✨ Analyze Job Match";

            }

        }
    );

}


/* =========================================================
   DISPLAY JOB MATCH RESULT
========================================================= */

function displayJobMatchResult(data) {

    if (!jobMatchResult) {
        return;
    }


    /* ---------- Score ---------- */

    const score =
        Number(
            data.match_score ??
            data.score ??
            0
        );


    const scoreElement =
        document.getElementById(
            "jobMatchScore"
        );


    if (scoreElement) {

        scoreElement.textContent =
            `${score}%`;

        updateJobScoreCircle(
            scoreElement,
            score
        );

    }


    /* ---------- Skills ---------- */

    renderSkills(
        "jobMatchedSkills",
        data.matched_skills || [],
        "skill-tag"
    );


    renderSkills(
        "jobMissingSkills",
        data.missing_skills || [],
        "skill-tag missing"
    );


    renderSkills(
        "jobResumeSkills",
        data.resume_skills || [],
        "skill-tag"
    );


    renderSkills(
        "jobRequiredSkills",
        data.job_skills || [],
        "skill-tag"
    );


    /* ---------- Recommendations ---------- */

    const recommendationList =
        document.getElementById(
            "jobRecommendations"
        );


    if (recommendationList) {

        recommendationList.innerHTML = "";

        const recommendations =
            data.recommendations || [];


        if (recommendations.length === 0) {

            const li =
                document.createElement("li");

            li.textContent =
                "Your resume is a strong match for this job.";

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


    /* ---------- Show result ---------- */

    jobMatchResult.classList.remove(
        "hidden"
    );


    jobMatchResult.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================================
   UPDATE SCORE CIRCLE
========================================================= */

function updateJobScoreCircle(
    element,
    score
) {

    const safeScore =
        Math.max(
            0,
            Math.min(100, score)
        );


    const degrees =
        safeScore * 3.6;


    element.style.background =
        `
        radial-gradient(
            circle,
            white 57%,
            transparent 58%
        ),
        conic-gradient(
            var(--primary) 0deg,
            var(--primary) ${degrees}deg,
            #dbe4f3 ${degrees}deg,
            #dbe4f3 360deg
        )
        `;

}


/* =========================================================
   JOB STATUS
========================================================= */

function showJobMatchStatus(
    message,
    type
) {

    if (!jobMatchStatus) {
        return;
    }


    jobMatchStatus.textContent =
        message;


    jobMatchStatus.className =
        "jd-status";


    if (type === "success") {

        jobMatchStatus.classList.add(
            "success"
        );

    } else if (type === "error") {

        jobMatchStatus.classList.add(
            "error"
        );

    }

}