/* =========================================================
   CAREERAI AUTHENTICATION
   FastAPI + JWT
   ========================================================= */

const API_BASE_URL = "https://career-ai-7m8h.onrender.com";


/* =========================================================
   LOGIN
   ========================================================= */

async function loginUser(email, password) {

    const response = await fetch(
        `${API_BASE_URL}/api/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        }
    );


    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Login failed. Please check your email and password."
        );

    }


    /*
     * FastAPI returns:
     *
     * {
     *     "access_token": "...",
     *     "token_type": "bearer"
     * }
     */

    if (!data.access_token) {

        throw new Error(
            "Login succeeded but no access token was returned."
        );

    }


    localStorage.setItem(
        "access_token",
        data.access_token
    );


    localStorage.setItem(
        "token_type",
        data.token_type || "bearer"
    );


    /*
     * Fetch the authenticated user's profile.
     */

    try {

        const userResponse = await fetch(
            `${API_BASE_URL}/api/users/me`,
            {
                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${data.access_token}`
                }
            }
        );


        if (userResponse.ok) {

            const user = await userResponse.json();

            localStorage.setItem(
                "user",
                JSON.stringify(user)
            );

        }

    } catch (error) {

        console.warn(
            "Could not fetch user profile:",
            error
        );

    }


    return data;
}


/* =========================================================
   REGISTER
   ========================================================= */

async function registerUser(
    name,
    email,
    password
) {

    const response = await fetch(
        `${API_BASE_URL}/api/auth/register`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        }
    );


    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Registration failed. Please try again."
        );

    }


    return data;
}


/* =========================================================
   LOGOUT
   ========================================================= */

function logoutUser() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "token_type"
    );

    localStorage.removeItem(
        "user"
    );


    window.location.href =
        "login.html";
}


/* =========================================================
   CHECK LOGIN
   ========================================================= */

function isLoggedIn() {

    return !!localStorage.getItem(
        "access_token"
    );
}


/* =========================================================
   GET JWT
   ========================================================= */

function getAccessToken() {

    return localStorage.getItem(
        "access_token"
    );
}


/* =========================================================
   AUTHENTICATED REQUEST HELPER
   ========================================================= */

async function authenticatedFetch(
    url,
    options = {}
) {

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        window.location.href =
            "login.html";

        throw new Error(
            "Authentication required."
        );
    }


    const headers = {
        ...(options.headers || {}),

        "Authorization":
            `Bearer ${token}`
    };


    const response = await fetch(
        url,
        {
            ...options,
            headers
        }
    );


    /*
     * JWT expired or invalid.
     */

    if (response.status === 401) {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "token_type"
        );

        localStorage.removeItem(
            "user"
        );


        window.location.href =
            "login.html";

        throw new Error(
            "Your session has expired. Please log in again."
        );
    }


    return response;
}


/* =========================================================
   PASSWORD VISIBILITY
   ========================================================= */

function togglePassword(
    inputId,
    button
) {

    const input =
        document.getElementById(inputId);


    if (!input) {
        return;
    }


    if (input.type === "password") {

        input.type = "text";

        button.textContent = "🙈";

    } else {

        input.type = "password";

        button.textContent = "👁";
    }
}


/* =========================================================
   PASSWORD STRENGTH
   ========================================================= */

function getPasswordStrength(password) {

    let score = 0;


    if (password.length >= 8) {
        score++;
    }

    if (/[A-Z]/.test(password)) {
        score++;
    }

    if (/[a-z]/.test(password)) {
        score++;
    }

    if (/[0-9]/.test(password)) {
        score++;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
        score++;
    }


    return score;
}


function updatePasswordStrength(
    password,
    container
) {

    if (!container) {
        return;
    }


    if (!password) {

        container.style.display =
            "none";

        return;
    }


    container.style.display =
        "block";


    const score =
        getPasswordStrength(password);


    const bars =
        container.querySelectorAll(
            ".strength-bar"
        );


    const text =
        container.querySelector(
            ".strength-text"
        );


    bars.forEach(
        (bar, index) => {

            if (index < score) {

                bar.style.background =
                    score <= 2
                        ? "#ef4444"
                        : score === 3
                            ? "#f59e0b"
                            : "#22c55e";

            } else {

                bar.style.background =
                    "#e2e8f0";
            }

        }
    );


    if (score <= 2) {

        text.textContent =
            "Weak password";

    } else if (score === 3) {

        text.textContent =
            "Moderate password";

    } else if (score === 4) {

        text.textContent =
            "Strong password";

    } else {

        text.textContent =
            "Very strong password";
    }
}


/* =========================================================
   MESSAGE
   ========================================================= */

function showAuthMessage(
    element,
    message,
    type = "error"
) {

    if (!element) {
        return;
    }


    element.textContent =
        message;


    element.className =
        `auth-message show ${type}`;
}


/* =========================================================
   LOGIN PAGE
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const loginForm =
            document.getElementById(
                "loginForm"
            );


        if (!loginForm) {
            return;
        }


        const emailInput =
            document.getElementById(
                "email"
            );


        const passwordInput =
            document.getElementById(
                "password"
            );


        const message =
            document.getElementById(
                "authMessage"
            );


        const button =
            document.getElementById(
                "loginButton"
            );


        loginForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();


                const email =
                    emailInput.value.trim();


                const password =
                    passwordInput.value;


                if (!email ||
                    !password) {

                    showAuthMessage(
                        message,
                        "Please enter your email and password."
                    );

                    return;
                }


                button.disabled = true;


                button.innerHTML = `
                    <span class="button-loading">
                        <span class="spinner"></span>
                        Signing you in...
                    </span>
                `;


                message.className =
                    "auth-message";


                try {

                    await loginUser(
                        email,
                        password
                    );


                    showAuthMessage(
                        message,
                        "Login successful. Opening your dashboard...",
                        "success"
                    );


                    setTimeout(
                        () => {
                            window.location.href = "../index.html";
                            

                        },
                        500
                    );


                } catch (error) {

                    showAuthMessage(
                        message,
                        error.message,
                        "error"
                    );


                    button.disabled = false;


                    button.innerHTML =
                        "Sign in →";
                }

            }
        );

    }
);


/* =========================================================
   REGISTER PAGE
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const registerForm =
            document.getElementById(
                "registerForm"
            );


        if (!registerForm) {
            return;
        }


        const nameInput =
            document.getElementById(
                "name"
            );


        const emailInput =
            document.getElementById(
                "email"
            );


        const passwordInput =
            document.getElementById(
                "password"
            );


        const confirmPasswordInput =
            document.getElementById(
                "confirmPassword"
            );


        const strengthContainer =
            document.getElementById(
                "passwordStrength"
            );


        const message =
            document.getElementById(
                "authMessage"
            );


        const button =
            document.getElementById(
                "registerButton"
            );


        passwordInput.addEventListener(
            "input",
            () => {

                updatePasswordStrength(
                    passwordInput.value,
                    strengthContainer
                );

            }
        );


        registerForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();


                const name =
                    nameInput.value.trim();


                const email =
                    emailInput.value.trim();


                const password =
                    passwordInput.value;


                const confirmPassword =
                    confirmPasswordInput.value;


                if (!name ||
                    !email ||
                    !password ||
                    !confirmPassword) {

                    showAuthMessage(
                        message,
                        "Please complete all fields."
                    );

                    return;
                }


                if (password.length < 8) {

                    showAuthMessage(
                        message,
                        "Password must contain at least 8 characters."
                    );

                    return;
                }


                if (password !== confirmPassword) {

                    showAuthMessage(
                        message,
                        "Passwords do not match."
                    );

                    return;
                }


                button.disabled = true;


                button.innerHTML = `
                    <span class="button-loading">
                        <span class="spinner"></span>
                        Creating account...
                    </span>
                `;


                message.className =
                    "auth-message";


                try {

                    await registerUser(
                        name,
                        email,
                        password
                    );


                    showAuthMessage(
                        message,
                        "Account created successfully. Redirecting to login...",
                        "success"
                    );


                    setTimeout(
                        () => {

                            window.location.href =
                                "login.html";

                        },
                        900
                    );


                } catch (error) {

                    showAuthMessage(
                        message,
                        error.message,
                        "error"
                    );


                    button.disabled = false;


                    button.innerHTML =
                        "Create my account →";
                }

            }
        );

    }
);