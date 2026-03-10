const API_BASE = "http://localhost:8000/api";

async function apiGet(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    return await res.json();
}

async function apiPost(endpoint, data) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    return await res.json();
}