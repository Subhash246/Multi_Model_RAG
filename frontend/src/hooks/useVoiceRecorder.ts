import { useCallback, useRef, useState } from "react";

/**
 * Wraps the browser MediaRecorder API. Returns a blob on stop, which the
 * caller can send to /api/v1/upload today, and later to a streaming STT
 * endpoint (Faster-Whisper, per the architecture doc) without changing
 * this hook's surface.
 */
export function useVoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const start = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch {
      setError("Microphone access was denied or is unavailable.");
    }
  }, []);

  const stop = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const recorder = mediaRecorderRef.current;
      if (!recorder) {
        resolve(null);
        return;
      }
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        recorder.stream.getTracks().forEach((track) => track.stop());
        setIsRecording(false);
        resolve(blob);
      };
      recorder.stop();
    });
  }, []);

  return { isRecording, error, start, stop };
}
