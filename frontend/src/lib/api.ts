import type { Attachment, ChatMessage } from "./types";

const API_BASE = "/api/v1";

export async function streamChat(
  messages: Pick<ChatMessage, "role" | "content">[],
  onToken: (token: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages,
      stream: true,
    }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, {
        stream: true,
      });

      const lines = buffer.split("\n");

      // Keep incomplete line for next chunk
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmedLine = line.trim();

        if (!trimmedLine.startsWith("data:")) {
          continue;
        }

        const payload = trimmedLine
          .slice("data:".length)
          .trim();

        if (payload === "[DONE]") {
          return;
        }

        if (payload) {
          let token = payload;

          try {
            const parsed = JSON.parse(payload) as {
              type?: string;
              content?: string;
            };

            if (
              parsed.type === "token" &&
              typeof parsed.content === "string"
            ) {
              token = parsed.content;
            }
          } catch {
            // Plain-text SSE payload (legacy format).
          }

          onToken(token.replace(/\\n/g, "\n"));
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function uploadFile(
  file: File,
): Promise<Attachment> {
  const form = new FormData();

  form.append("file", file);

  const response = await fetch(
    `${API_BASE}/upload`,
    {
      method: "POST",
      body: form,
    },
  );

  if (!response.ok) {
    let detail = `Upload failed: ${response.status}`;

    try {
      const body = await response.json();

      if (body?.detail) {
        detail = body.detail;
      }
    } catch {
      // Ignore invalid error responses.
    }

    throw new Error(detail);
  }

  return response.json() as Promise<Attachment>;
}