import { useState, useRef, useCallback } from "react";

const CHUNK_DURATION_MS = 10000;

function useChunkedRecorder(onChunkReady) {
    const [isRecording, setIsRecording] = useState(false);
    const streamRef = useRef(null);
    const recorderRef = useRef(null);
    const timeoutRef = useRef(null);
    const isRecordingRef = useRef(false);

    const startChunkCycle = useCallback(() => {
        if (!isRecordingRef.current || !streamRef.current) return

        const recorder = new MediaRecorder(streamRef.current, {mimeType: "audio/webm"});
        const chunks = [];

        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };

        recorder.onstop = () => {
            const blob = new Blob(chunks, { type: "audio/webm"});
            if (blob.size > 0) onChunkReady(blob);

            if (isRecordingRef.current) {
                startChunkCycle();
            }
        };

        recorder.start();
        recorderRef.current = recorder;

        timeoutRef.current = setTimeout(() => {
            recorder.stop();
        }, CHUNK_DURATION_MS);
    }, [onChunkReady]);

    const startRecording = useCallback(async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        isRecordingRef.current = true;
        setIsRecording(true);
        startChunkCycle();
    }, [startChunkCycle]);

    const stopRecording = useCallback(async () => {
        isRecordingRef.current = false;
        setIsRecording(false);

        clearTimeout(timeoutRef.current);
        if (recorderRef.current && recorderRef.current.state != "inactive") {
            recorderRef.current.stop();
        }
        streamRef.current?.getTracks().forEach((track) => track.stop());
    }, []);

    return { isRecording, startRecording, stopRecording };
}

export default useChunkedRecorder;