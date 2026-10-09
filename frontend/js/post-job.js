/* =========================================================
   CAREERAI - POST A JOB
   Recruiter job publishing
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

const postJobForm =
    document.getElementById("postJobForm");

const publishButton =
    document.getElementById("publishButton");

const formStatus =
    document.getElementById("formStatus");


/* =========================================================
   STATUS MESSAGE
========================================================= */

function showStatus(message, type) {

    if (!formStatus) {
        return;
    }

    formStatus.textContent = message;

    formStatus.className =
        "form-status show";

    if (type === "success") {

        formStatus.classList.add("success");

    } else if (type === "error") {

        formStatus.classList.add("error");

    } else {

        formStatus.classList.add("loading");
    }
}


/* =========================================================
   HIDE STATUS
========================================================= */

function hideStatus() {

    if (!formStatus) {
        return;
    }

    formStatus.textContent = "";

    formStatus.className =
        "form-status";
}


/* =========================================================
   FORM SUBMIT
========================================================= */

if (postJobForm) {

    postJobForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            hideStatus();


            /* -------------------------------------------------
               AUTHENTICATION
            ------------------------------------------------- */

            const token =
                getAuthToken();

            if (!token) {

                showStatus(
                    "Your session has expired. Please login again.",
                    "error"
                );

                return;
            }


            /* -------------------------------------------------
               READ FORM VALUES
            ------------------------------------------------- */

            const title =
                document
                    .getElementById("jobTitle")
                    .value
                    .trim();

            const company =
                document
                    .getElementById("company")
                    .value
                    .trim();

            const location =
                document
                    .getElementById("location")
                    .value
                    .trim();

            const jobType =
                document
                    .getElementById("jobType")
                    .value
                    .trim();

            const salary =
                document
                    .getElementById("salary")
                    .value
                    .trim();

            const experience =
                document
                    .getElementById("experience")
                    .value
                    .trim();

            const skills =
                document
                    .getElementById("skills")
                    .value
                    .trim();

            const description =
                document
                    .getElementById("description")
                    .value
                    .trim();

            const applicationUrl =
                document
                    .getElementById("applicationUrl")
                    .value
                    .trim();


            /* -------------------------------------------------
               BASIC VALIDATION
            ------------------------------------------------- */

            if (!title) {

                showStatus(
                    "Please enter the job title.",
                    "error"
                );

                return;
            }

            if (!company) {

                showStatus(
                    "Please enter the company name.",
                    "error"
                );

                return;
            }

            if (!location) {

                showStatus(
                    "Please enter the job location.",
                    "error"
                );

                return;
            }

            if (!jobType) {

                showStatus(
                    "Please select the job type.",
                    "error"
                );

                return;
            }

            if (!skills) {

                showStatus(
                    "Please enter at least one required skill.",
                    "error"
                );

                return;
            }

            if (!description) {

                showStatus(
                    "Please enter the job description.",
                    "error"
                );

                return;
            }


            /* -------------------------------------------------
               DISABLE BUTTON
            ------------------------------------------------- */

            publishButton.disabled = true;

            publishButton.textContent =
                "Publishing Job...";


            showStatus(
                "Creating your job listing...",
                "loading"
            );


            /* -------------------------------------------------
               PREPARE JOB DATA
            ------------------------------------------------- */

            const jobData = {

                title: title,

                company: company,

                location: location,

                job_type: jobType,

                salary: salary || null,

                experience: experience || null,

                skills: skills,

                description: description,

                application_url:
                    applicationUrl || null
            };


            console.log(
                "Publishing job:",
                jobData
            );


            /* -------------------------------------------------
               API REQUEST
            ------------------------------------------------- */

            try {

                const response =
                    await fetch(
                        `${API_BASE_URL}/api/jobs/`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body:
                                JSON.stringify(
                                    jobData
                                )
                        }
                    );


                /* -------------------------------------------------
                   READ RESPONSE
                ------------------------------------------------- */

                const data =
                    await response.json();


                console.log(
                    "Job API response:",
                    data
                );


                /* -------------------------------------------------
                   ERROR
                ------------------------------------------------- */

                if (!response.ok) {

                    let errorMessage =
                        "Unable to publish the job.";

                    if (data.detail) {

                        if (
                            typeof data.detail ===
                            "string"
                        ) {

                            errorMessage =
                                data.detail;

                        } else {

                            errorMessage =
                                "The job information is invalid.";
                        }
                    }

                    throw new Error(
                        errorMessage
                    );
                }


                /* -------------------------------------------------
                   SUCCESS
                ------------------------------------------------- */

                showStatus(
                    "🎉 Job published successfully!",
                    "success"
                );


                publishButton.textContent =
                    "✓ Job Published";


                /* -------------------------------------------------
                   CLEAR FORM
                ------------------------------------------------- */

                postJobForm.reset();


                /* -------------------------------------------------
                   REDIRECT
                -------------------------------------------------

                   Wait a little so the user can
                   see the success message.
                */

                setTimeout(
                    function () {

                        window.location.href =
                            "jobs.html";

                    },
                    1200
                );


            } catch (error) {

                console.error(
                    "Post job error:",
                    error
                );


                showStatus(
                    error.message ||
                    "Something went wrong while publishing the job.",
                    "error"
                );


                publishButton.disabled =
                    false;

                publishButton.textContent =
                    "🚀 Publish Job";
            }

        }
    );
}