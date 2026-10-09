/* =========================================================
   CAREERAI - DASHBOARD
========================================================= */

const DASHBOARD_API =
    "http://127.0.0.1:8000";


/* =========================================================
   GET TOKEN
========================================================= */

function getDashboardToken() {

    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        localStorage.getItem("jwt")
    );

}


/* =========================================================
   LOGOUT
========================================================= */

function logoutUser() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    localStorage.removeItem("jwt");

    window.location.href =
        "login.html";

}


/* =========================================================
   OPEN PAGE
========================================================= */

function openPage(page) {

    window.location.href = page;

}


/* =========================================================
   LOAD USER
========================================================= */

async function loadDashboardUser() {

    const token =
        getDashboardToken();


    if (!token) {

        window.location.href =
            "login.html";

        return;

    }


    try {

        const response =
            await fetch(
                `${DASHBOARD_API}/api/users/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`,

                        "Accept":
                            "application/json"
                    }
                }
            );


        console.log(
            "User API status:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                `User API returned ${response.status}`
            );

        }


        const user =
            await response.json();
            // Save the logged-in user's role for dashboard UI
const userRole = (user.role || "user").toLowerCase();

console.log("Logged-in user role:", userRole);

// Show admin-only dashboard elements
document.querySelectorAll(".admin-only").forEach((element) => {
    element.style.display = userRole === "admin" ? "" : "none";
});



        console.log(
            "Logged-in user:",
            user
        );


        const name =
            user.name ||
            "Career Explorer";


        const userName =
            document.getElementById(
                "userName"
            );


        const welcomeName =
            document.getElementById(
                "welcomeName"
            );


        if (userName) {

            userName.textContent =
                name;

        }


        if (welcomeName) {

            welcomeName.textContent =
                name;

        }


    }

    catch (error) {

        console.error(
            "User loading error:",
            error
        );

    }

}


/* =========================================================
   LOAD DASHBOARD DATA
========================================================= */

async function loadDashboardData() {

    const token =
        getDashboardToken();


    if (!token) {

        window.location.href =
            "login.html";

        return;

    }


    try {

        const response =
            await fetch(
                `${DASHBOARD_API}/api/dashboard/`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`,

                        "Accept":
                            "application/json"
                    }
                }
            );


        console.log(
            "Dashboard API status:",
            response.status
        );


        const data =
            await response.json();


        console.log(
            "Dashboard data:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Dashboard API returned ${response.status}`
            );

        }


        /* =============================================
           RESUME SCORE
        ============================================== */

        const resumeScore =
            document.getElementById(
                "resumeScore"
            );


        if (resumeScore) {

            resumeScore.textContent =
                data.latest_score !== null &&
                data.latest_score !== undefined

                    ? `${data.latest_score}%`

                    : "—";

        }


        /* =============================================
           JOB MATCHES
        ============================================== */

        const jobMatches =
            document.getElementById(
                "jobMatches"
            );


        if (jobMatches) {

            jobMatches.textContent =
                data.available_jobs ??
                0;

        }


        /* =============================================
           SKILLS
        ============================================== */

        const skillsIdentified =
            document.getElementById(
                "skillsIdentified"
            );


        if (skillsIdentified) {

            const matched =
                Number(
                    data.total_matched_skills ||
                    0
                );


            const missing =
                Number(
                    data.total_missing_skills ||
                    0
                );


            skillsIdentified.textContent =
                matched + missing;

        }


        /* =============================================
           APPLICATIONS
        ============================================== */

        const applicationsCount =
            document.getElementById(
                "applicationsCount"
            );


        if (applicationsCount) {

            applicationsCount.textContent =
                data.application_count ??
                0;

        }


    }

    catch (error) {

        console.error(
            "Dashboard data error:",
            error
        );

    }

}


/* =========================================================
   INITIALIZE
========================================================= */

async function initializeDashboard() {

    console.log(
        "================================="
    );

    console.log(
        "CareerAI Dashboard starting..."
    );

    console.log(
        "================================="
    );


    const token =
        getDashboardToken();


    console.log(
        "Token exists:",
        Boolean(token)
    );


    if (!token) {

        console.log(
            "No JWT token found."
        );


        window.location.href =
            "login.html";


        return;

    }


    await loadDashboardUser();

    await loadDashboardData();


    console.log(
        "CareerAI Dashboard loaded."
    );

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);