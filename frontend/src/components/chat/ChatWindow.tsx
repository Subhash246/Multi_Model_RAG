import { useEffect, useRef } from "react";

import type { ChatMessage } from "../../lib/types";
import { EmptyState } from "./EmptyState";
import { MessageBubble } from "./MessageBubble";

interface ChatWindowProps {
  messages: ChatMessage[];
  onRetry?: (messageId: string) => void;
  onEdit?: (messageId: string, newText: string) => void;
  disabled?: boolean;
}

export function ChatWindow({
  messages,
  onRetry,
  onEdit,
  disabled = false,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <EmptyState />
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRetry={onRetry}
            onEdit={onEdit}
            disabled={disabled}
          />
        ))}
        <div ref={bottomRef} />
      </div>
    </main>
  );
}
