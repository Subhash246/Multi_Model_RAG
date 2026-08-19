import { useRef, useState, type ChangeEvent, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { ArrowUp, Mic, Paperclip, Square, X } from "lucide-react";
import clsx from "clsx";
import { useAutoResizeTextarea } from "../../hooks/useAutoResizeTextarea";
import { useVoiceRecorder } from "../../hooks/useVoiceRecorder";
import { uploadFile } from "../../lib/api";

import type {
  Attachment,
  PendingAttachment,
} from "../../lib/types";
import { AttachmentChip } from "./AttachmentChip";

interface Props {
  onSend: (text: string, attachments: Attachment[]) => void;
  isStreaming: boolean;
  onStop: () => void;
}

export function ChatInput({ onSend, isStreaming, onStop }: Props) {
  const [text, setText] = useState("");
  const [attachments, setAttachments] = useState<PendingAttachment[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useAutoResizeTextarea(text);
  const { isRecording, error: micError, start, stop } = useVoiceRecorder();

  const canSend = (text.trim().length > 0 || attachments.length > 0) && !isStreaming && !isUploading;

  async function handleSend() {
    if (!canSend) {
      return;
    }
  
    setIsUploading(true);
  
    try {
      // --------------------------------------------------
      // 1. Upload selected files
      // --------------------------------------------------
  
      const uploadedAttachments: Attachment[] =
        await Promise.all(
          attachments.map(
            (attachment) =>
              uploadFile(attachment.file)
          )
        );
  
      // --------------------------------------------------
      // 2. Process uploaded documents
      // --------------------------------------------------
  
  
      // --------------------------------------------------
      // 3. Now send the chat message
      // --------------------------------------------------
  
      onSend(
        text,
        uploadedAttachments
      );
  
      // --------------------------------------------------
      // 4. Clear composer
      // --------------------------------------------------
  
      setText("");
      setAttachments([]);
  
    } catch (error) {
      console.error(
        "Failed to upload/process attachment:",
        error
      );
  
      // Keep attachments visible so the user
      // can retry instead of silently losing them.
    } finally {
      setIsUploading(false);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleFilesSelected(
    e: ChangeEvent<HTMLInputElement>
  ) {
    const files = Array.from(
      e.target.files ?? []
    );
  
    e.target.value = "";
  
    if (files.length === 0) {
      return;
    }
  
    const pendingFiles: PendingAttachment[] =
      files.map((file) => ({
        local_id: crypto.randomUUID(),
        file,
        filename: file.name,
        content_type:
          file.type || "application/octet-stream",
        size_bytes: file.size,
      }));
  
    setAttachments((prev) => [
      ...prev,
      ...pendingFiles,
    ]);
  }

  async function handleMicClick() {
    if (isRecording) {
      const blob = await stop();
  
      if (blob) {
        const file = new File(
          [blob],
          `voice-note-${Date.now()}.webm`,
          {
            type: "audio/webm",
          }
        );
  
        const pendingAttachment: PendingAttachment = {
          local_id: crypto.randomUUID(),
          file,
          filename: file.name,
          content_type: file.type,
          size_bytes: file.size,
        };
  
        setAttachments((prev) => [
          ...prev,
          pendingAttachment,
        ]);
      }
    } else {
      start();
    }
  }

  return (
    <div className="border-t border-border-light dark:border-border-dark px-6 pb-6 pt-3">
      <div className="mx-auto max-w-3xl">
        {micError && <p className="mb-2 text-xs text-red-500">{micError}</p>}

        <motion.div
          layout
          className={clsx(
            "flex flex-col gap-2 rounded-2xl border bg-surface-light dark:bg-surface-dark px-3 py-2.5",
            "border-border-light dark:border-border-dark shadow-floating",
            "transition-colors focus-within:border-accent-from/60",
          )}
        >
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-1.5 px-1 pt-0.5">
              {attachments.map((a) => (
                <AttachmentChip
                  key={a.local_id}
                  attachment={a}
                  onRemove={() => setAttachments((prev) => prev.filter((x) => x.local_id !== a.local_id))}
                />
              ))}
            </div>
          )}

          <div className="flex items-end gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              aria-label="Attach files"
              disabled={isStreaming}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full
                         text-muted-light dark:text-muted-dark
                         hover:bg-canvas-light dark:hover:bg-canvas-dark hover:text-ink-light dark:hover:text-ink-dark
                         transition-colors disabled:opacity-40"
            >
              <Paperclip size={18} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              onChange={handleFilesSelected}
              accept=".pdf,.docx,.doc,.txt,.md,.png,.jpg,.jpeg,.mp3,.wav,.mp4,.m4a"
            />

            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isRecording ? "Listening…" : "Message the assistant…"}
              rows={1}
              disabled={isRecording}
              className="flex-1 resize-none bg-transparent py-1.5 text-[15px] leading-relaxed
                         placeholder:text-muted-light dark:placeholder:text-muted-dark
                         focus:outline-none disabled:opacity-60"
            />

            <button
              onClick={handleMicClick}
              aria-label={isRecording ? "Stop recording" : "Record voice message"}
              className={clsx(
                "relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-colors",
                isRecording
                  ? "bg-red-500/10 text-red-500"
                  : "text-muted-light dark:text-muted-dark hover:bg-canvas-light dark:hover:bg-canvas-dark hover:text-ink-light dark:hover:text-ink-dark",
              )}
            >
              {isRecording && (
                <motion.span
                  className="absolute inset-0 rounded-full bg-red-500/20"
                  animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0, 0.6] }}
                  transition={{ duration: 1.4, repeat: Infinity }}
                />
              )}
              <Mic size={18} className="relative" />
            </button>

            {isStreaming ? (
              <button
                onClick={onStop}
                aria-label="Stop generating"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full
                           bg-ink-light dark:bg-ink-dark text-canvas-light dark:text-canvas-dark
                           transition-transform hover:scale-105"
              >
                <Square size={14} fill="currentColor" />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!canSend}
                aria-label="Send message"
                className={clsx(
                  "flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all",
                  canSend
                    ? "accent-gradient text-white hover:scale-105 shadow-floating"
                    : "bg-canvas-light dark:bg-canvas-dark text-muted-light dark:text-muted-dark cursor-not-allowed",
                )}
              >
                <ArrowUp size={18} />
              </button>
            )}
          </div>
        </motion.div>

        <p className="mt-2 text-center text-[11px] text-muted-light dark:text-muted-dark">
          The assistant can be wrong. Verify important information.
        </p>
      </div>
    </div>
  );
}

// Re-exported so future toolbar additions (e.g. a "clear attachments" X)
// can reuse the same icon without importing lucide-react everywhere.
export { X as ClearIcon };
