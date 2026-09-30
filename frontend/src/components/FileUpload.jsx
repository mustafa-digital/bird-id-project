// src/components/FileUpload.jsx

import { useRef, useState } from "react"
import { predictSpecies } from "../services/api"

const ACCEPTED_TYPES = ".mp3,.wav,.webm,.m4a,.ogg,audio/mpeg,audio/wav,audio/x-wav,audio/webm,audio/mp4,audio/ogg";

function FileUpload({ onPrediction, onError }) {
    const inputRef = useRef(null);
    const [isUploading, setIsUploading] = useState(false);

    const handleFileChange = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return

        setIsUploading(true);
        try {
            const result = await predictSpecies(file);
            onPrediction(result);
        } catch (err) {
            console.error("Upload failed: ", err);
            onError(err.message || "Upload failed");
        } finally {
            setIsUploading(false);
            e.target.value = "";
        }
    };

    return (
        <>
            <input
                ref={inputRef}
                type="file"
                accept={ACCEPTED_TYPES}
                onChange={handleFileChange}
                style={{ display: "none" }}
            />
            <button
                onClick={() => inputRef.current?.click()}
                disabled={isUploading}
                className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
                {isUploading ? "Analyzing audio..." : "Upload audio file"}
            </button>
        </>
    );
}

export default FileUpload;