const API_BASE_URL = "http://127.0.0.1:8000/api";


async function apiRequest(endpoint, options = {}) {

    const token = localStorage.getItem("access_token");

    const headers = {
        ...(options.headers || {})
    };

    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");

            window.location.href = "login.html";
            return;
        }

        throw new Error(
            data?.detail || "Something went wrong"
        );
    }

    return data;
}