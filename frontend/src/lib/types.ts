export type Role = "user" | "assistant" | "system";

export interface Attachment {
  file_id: string;
  filename: string;
  content_type: string;
  size_bytes?: number;
  status?: "uploaded" | "queued" | "processing" | "ready" | "failed";
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  attachments?: Attachment[];
  isStreaming?: boolean;
}
