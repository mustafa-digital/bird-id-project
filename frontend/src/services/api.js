// src/services/api.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function predictSpecies(audioBlob) {
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "chunk.webm");

    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }
    const response_json = await response.json()
    return response_json
}

export async function queryLLM(query, message_history) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, message_history })
    })

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }
    return response.json()

}
