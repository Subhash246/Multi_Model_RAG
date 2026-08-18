import { useState } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Check,
  Copy,
  Pencil,
  RotateCcw,
  X,
} from "lucide-react";

import type { ChatMessage } from "../../lib/types";
import { AttachmentChip } from "./AttachmentChip";

interface Props {
  message: ChatMessage;
  onRetry?: (messageId: string) => void;
  onEdit?: (messageId: string, newText: string) => void;
  disabled?: boolean;
}

export function MessageBubble({
  message,
  onRetry,
  onEdit,
  disabled = false,
}: Props) {
  const isUser = message.role === "user";

  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(message.content);
  const [copied, setCopied] = useState(false);

  /*
   * ---------------------------------------------------------
   * COPY
   * ---------------------------------------------------------
   */
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);

      setCopied(true);

      window.setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch {
      // Clipboard access may be unavailable.
    }
  };

  /*
   * ---------------------------------------------------------
   * EDIT
   * ---------------------------------------------------------
   */
  const handleEditStart = () => {
    setEditText(message.content);
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    setEditText(message.content);
    setIsEditing(false);
  };

  const handleEditSubmit = () => {
    const trimmed = editText.trim();

    if (!trimmed) return;

    setIsEditing(false);

    onEdit?.(message.id, trimmed);
  };

  /*
   * ---------------------------------------------------------
   * RETRY
   * ---------------------------------------------------------
   */
  const handleRetry = () => {
    if (disabled || message.isStreaming) return;

    onRetry?.(message.id);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.3,
        ease: "easeOut",
      }}
      className={clsx(
        "flex w-full",
        isUser
          ? "justify-end"
          : "justify-start"
      )}
    >
      <div
        className={clsx(
          "flex flex-col",
          isUser
            ? "max-w-[650px] items-end"
            : "w-full max-w-[1050px]"
        )}
      >
        {/* -------------------------------------------------- */}
        {/* ATTACHMENTS */}
        {/* -------------------------------------------------- */}

        {message.attachments &&
          message.attachments.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-1.5">
              {message.attachments.map((a) => (
                <AttachmentChip
                  key={a.file_id}
                  attachment={a}
                />
              ))}
            </div>
          )}

        {/* -------------------------------------------------- */}
        {/* USER MESSAGE */}
        {/* -------------------------------------------------- */}

        {isUser ? (
          <>
            {isEditing ? (
              /*
               * EDIT MODE
               */
              <div className="w-full max-w-[650px]">
                <textarea
                  value={editText}
                  onChange={(e) =>
                    setEditText(e.target.value)
                  }
                  autoFocus
                  rows={3}
                  disabled={disabled}
                  className="
                    w-full
                    resize-none
                    rounded-2xl
                    border
                    border-border-light
                    bg-canvas-light
                    px-4
                    py-3
                    text-[15px]
                    leading-relaxed
                    text-ink-light
                    outline-none
                    transition
                    focus:border-accent-from
                    dark:border-border-dark
                    dark:bg-canvas-dark
                    dark:text-ink-dark
                  "
                />

                {/* EDIT ACTIONS */}
                <div className="mt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={handleEditCancel}
                    disabled={disabled}
                    className="
                      inline-flex
                      items-center
                      gap-1.5
                      rounded-lg
                      px-3
                      py-1.5
                      text-sm
                      text-muted-light
                      transition
                      hover:bg-canvas-light
                      hover:text-ink-light
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                      dark:text-muted-dark
                      dark:hover:bg-surface-dark
                      dark:hover:text-ink-dark
                    "
                  >
                    <X size={15} />
                    Cancel
                  </button>

                  <button
                    type="button"
                    onClick={handleEditSubmit}
                    disabled={
                      disabled ||
                      !editText.trim()
                    }
                    className="
                      inline-flex
                      items-center
                      gap-1.5
                      rounded-lg
                      bg-accent-from
                      px-3
                      py-1.5
                      text-sm
                      font-medium
                      text-white
                      transition
                      hover:opacity-90
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                    "
                  >
                    <Check size={15} />
                    Submit
                  </button>
                </div>
              </div>
            ) : (
              /*
               * NORMAL USER MESSAGE
               */
              <>
                <div
                  className="
                    accent-gradient
                    rounded-2xl
                    rounded-br-md
                    px-4
                    py-3
                    text-[15px]
                    leading-relaxed
                    text-white
                    break-words
                  "
                >
                  <p className="whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>

                {/* -------------------------------------------------- */}
                {/* USER MESSAGE ACTIONS */}
                {/* -------------------------------------------------- */}

                <div
                  className="
                    mt-1.5
                    flex
                    items-center
                    gap-1
                    pr-1
                  "
                >
                  {/* COPY */}
                  <button
                    type="button"
                    onClick={handleCopy}
                    disabled={disabled}
                    title={
                      copied
                        ? "Copied"
                        : "Copy message"
                    }
                    aria-label={
                      copied
                        ? "Copied"
                        : "Copy message"
                    }
                    className="
                      rounded-md
                      p-1.5
                      text-muted-light
                      transition
                      hover:bg-surface-light
                      hover:text-ink-light
                      disabled:cursor-not-allowed
                      disabled:opacity-40
                      dark:text-muted-dark
                      dark:hover:bg-surface-dark
                      dark:hover:text-ink-dark
                    "
                  >
                    {copied ? (
                      <Check size={16} />
                    ) : (
                      <Copy size={16} />
                    )}
                  </button>

                  {/* EDIT */}
                  <button
                    type="button"
                    onClick={handleEditStart}
                    disabled={
                      disabled ||
                      message.isStreaming
                    }
                    title="Edit message"
                    aria-label="Edit message"
                    className="
                      rounded-md
                      p-1.5
                      text-muted-light
                      transition
                      hover:bg-surface-light
                      hover:text-ink-light
                      disabled:cursor-not-allowed
                      disabled:opacity-40
                      dark:text-muted-dark
                      dark:hover:bg-surface-dark
                      dark:hover:text-ink-dark
                    "
                  >
                    <Pencil size={16} />
                  </button>

                  {/* RETRY */}
                  <button
                    type="button"
                    onClick={handleRetry}
                    disabled={
                      disabled ||
                      message.isStreaming
                    }
                    title="Retry response"
                    aria-label="Retry response"
                    className="
                      rounded-md
                      p-1.5
                      text-muted-light
                      transition
                      hover:bg-surface-light
                      hover:text-ink-light
                      disabled:cursor-not-allowed
                      disabled:opacity-40
                      dark:text-muted-dark
                      dark:hover:bg-surface-dark
                      dark:hover:text-ink-dark
                    "
                  >
                    <RotateCcw size={16} />
                  </button>
                </div>
              </>
            )}
          </>
        ) : (
          /* -------------------------------------------------- */
          /* ASSISTANT MESSAGE */
          /* -------------------------------------------------- */

          <div
            className="
              text-[15px]
              leading-relaxed
              text-ink-light
              break-words
              dark:text-ink-dark
            "
          >
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  /* ---------------- PARAGRAPH ---------------- */

                  p: ({ node, ...props }) => (
                    <p
                      className="
                        mb-3
                        last:mb-0
                        leading-relaxed
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- UNORDERED LIST ---------------- */

                  ul: ({ node, ...props }) => (
                    <ul
                      className="
                        mb-3
                        list-disc
                        space-y-1
                        pl-5
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- ORDERED LIST ---------------- */

                  ol: ({ node, ...props }) => (
                    <ol
                      className="
                        mb-3
                        list-decimal
                        space-y-1
                        pl-5
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- LIST ITEM ---------------- */

                  li: ({ node, ...props }) => (
                    <li
                      className="leading-relaxed"
                      {...props}
                    />
                  ),

                  /* ---------------- H1 ---------------- */

                  h1: ({ node, ...props }) => (
                    <h1
                      className="
                        mb-3
                        mt-5
                        text-xl
                        font-bold
                        first:mt-0
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- H2 ---------------- */

                  h2: ({ node, ...props }) => (
                    <h2
                      className="
                        mb-3
                        mt-5
                        text-lg
                        font-bold
                        first:mt-0
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- H3 ---------------- */

                  h3: ({ node, ...props }) => (
                    <h3
                      className="
                        mb-2
                        mt-4
                        text-base
                        font-semibold
                        first:mt-0
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- TABLE ---------------- */

                  table: ({ node, ...props }) => (
                    <div
                      className="
                        my-4
                        w-full
                        overflow-x-auto
                      "
                    >
                      <table
                        className="
                          w-full
                          border-collapse
                          text-left
                          text-sm
                        "
                        {...props}
                      />
                    </div>
                  ),

                  /* ---------------- TABLE HEADER ---------------- */

                  th: ({ node, ...props }) => (
                    <th
                      className="
                        border
                        border-border-light
                        px-3
                        py-2
                        font-semibold
                        dark:border-border-dark
                      "
                      {...props}
                    />
                  ),

                  /* ---------------- TABLE CELL ---------------- */

                  td: ({ node, ...props }) => (
                    <td
                      className="
                        border
                        border-border-light
                        px-3
                        py-2
                        dark:border-border-dark
                      "
                      {...props}
                    />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* -------------------------------------------------- */}
        {/* TYPING INDICATOR */}
        {/* -------------------------------------------------- */}

        {message.isStreaming &&
          !message.content && (
            <TypingDots />
          )}

        {/* -------------------------------------------------- */}
        {/* STREAMING CURSOR */}
        {/* -------------------------------------------------- */}

        {message.isStreaming &&
          message.content && (
            <BlinkingCursor />
          )}
      </div>
    </motion.div>
  );
}

/* ========================================================= */
/* TYPING DOTS                                                */
/* ========================================================= */

function TypingDots() {
  return (
    <span className="flex items-center gap-1 py-0.5">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="
            h-1.5
            w-1.5
            rounded-full
            bg-muted-light
            dark:bg-muted-dark
          "
          animate={{
            opacity: [0.3, 1, 0.3],
          }}
          transition={{
            duration: 1.1,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}
    </span>
  );
}

/* ========================================================= */
/* BLINKING CURSOR                                            */
/* ========================================================= */

function BlinkingCursor() {
  return (
    <motion.span
      className="
        ml-0.5
        inline-block
        h-3.5
        w-[2px]
        translate-y-[2px]
        bg-accent-from
      "
      animate={{
        opacity: [1, 0],
      }}
      transition={{
        duration: 0.7,
        repeat: Infinity,
        repeatType: "reverse",
      }}
    />
  );
}