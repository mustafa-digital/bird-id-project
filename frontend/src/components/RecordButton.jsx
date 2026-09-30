import { predictSpecies } from "../services/api";
import useChunkedRecorder from "../hooks/useChunkedRecorder";

function RecordButton({ onPrediction, onError }) {
    const uploadChunk = async (blob) => {

        try {
            const result = await predictSpecies(blob);
            // const predictions = result["predictions"];
            onPrediction(result);
        } catch (err) {
            console.error("Upload failed: ", err);
            onError(err.message || "Upload failed");
        }
    };

    const { isRecording, startRecording, stopRecording } = useChunkedRecorder(uploadChunk);

    return (
        <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm transition ${
                isRecording
                    ? "bg-red-600 hover:bg-red-700"
                    : "bg-indigo-600 hover:bg-indigo-700"
            }`}
        >
            {isRecording ? "Stop" : "Start Recording"}
        </button>
    )
}

export default RecordButton;