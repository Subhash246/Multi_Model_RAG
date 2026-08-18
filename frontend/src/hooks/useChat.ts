import {
  useCallback,
  useRef,
  useState,
} from "react";

import { streamChat } from "../lib/api";
import type {
  Attachment,
  ChatMessage,
} from "../lib/types"; // '../../lib/types'

function makeId() {
  return crypto.randomUUID();
}

export function useChat() {
  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [isStreaming, setIsStreaming] =
    useState(false);

  const abortRef =
    useRef<AbortController | null>(null);

  /*
   * =========================================================
   * GENERATE RESPONSE
   * =========================================================
   *
   * Shared by:
   * - Normal message
   * - Retry
   * - Edit
   */
  const generateResponse = useCallback(
    async (
      history: ChatMessage[],
      assistantId: string,
    ) => {
      const controller =
        new AbortController();

      abortRef.current = controller;

      setIsStreaming(true);

      try {
        const requestMessages =
          history.map(
            ({ role, content }) => ({
              role,
              content,
            }),
          );

        await streamChat(
          requestMessages,
          (token) => {
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      content:
                        message.content + token,
                    }
                  : message,
              ),
            );
          },
          controller.signal,
        );
      } catch (err) {
        /*
         * AbortError is expected when the user
         * presses Stop.
         */
        if (
          (err as Error).name !==
          "AbortError"
        ) {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content:
                      "Something went wrong reaching the model. Check that the backend and LiteLLM proxy are running.",
                  }
                : message,
            ),
          );
        }
      } finally {
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  isStreaming: false,
                }
              : message,
          ),
        );

        setIsStreaming(false);

        if (
          abortRef.current === controller
        ) {
          abortRef.current = null;
        }
      }
    },
    [],
  );

  /*
   * =========================================================
   * NORMAL SEND
   * =========================================================
   */
  const sendMessage = useCallback(
    async (
      text: string,
      attachments: Attachment[] = [],
    ) => {
      const trimmed = text.trim();

      if (
        !trimmed &&
        attachments.length === 0
      ) {
        return;
      }

      if (isStreaming) {
        return;
      }

      const userMessage: ChatMessage = {
        id: makeId(),
        role: "user",
        content: trimmed,
        attachments,
      };

      const assistantMessage: ChatMessage =
        {
          id: makeId(),
          role: "assistant",
          content: "",
          isStreaming: true,
        };

      const historyBeforeResponse = [
        ...messages,
        userMessage,
      ];

      setMessages([
        ...historyBeforeResponse,
        assistantMessage,
      ]);

      await generateResponse(
        historyBeforeResponse,
        assistantMessage.id,
      );
    },
    [
      messages,
      generateResponse,
      isStreaming,
    ],
  );

  /*
   * =========================================================
   * RETRY
   * =========================================================
   *
   * Regenerates the response for the
   * selected user message.
   */
  const retryMessage = useCallback(
    async (messageId: string) => {
      if (isStreaming) {
        return;
      }

      const index = messages.findIndex(
        (message) =>
          message.id === messageId,
      );

      if (index === -1) {
        return;
      }

      const selectedMessage =
        messages[index];

      /*
       * Retry only applies to user messages.
       */
      if (
        selectedMessage.role !== "user"
      ) {
        return;
      }

      /*
       * Keep everything up to and including
       * the selected user message.
       *
       * Remove the old assistant response
       * and anything after it.
       */
      const historyBeforeResponse =
        messages.slice(0, index + 1);

      const assistantMessage: ChatMessage =
        {
          id: makeId(),
          role: "assistant",
          content: "",
          isStreaming: true,
        };

      setMessages([
        ...historyBeforeResponse,
        assistantMessage,
      ]);

      await generateResponse(
        historyBeforeResponse,
        assistantMessage.id,
      );
    },
    [
      messages,
      generateResponse,
      isStreaming,
    ],
  );

  /*
   * =========================================================
   * EDIT
   * =========================================================
   *
   * Replaces the selected user message and
   * regenerates the conversation from that point.
   */
  const editMessage = useCallback(
    async (
      messageId: string,
      newText: string,
    ) => {
      if (isStreaming) {
        return;
      }

      const trimmed =
        newText.trim();

      if (!trimmed) {
        return;
      }

      const index = messages.findIndex(
        (message) =>
          message.id === messageId,
      );

      if (index === -1) {
        return;
      }

      const selectedMessage =
        messages[index];

      /*
       * Edit only applies to user messages.
       */
      if (
        selectedMessage.role !== "user"
      ) {
        return;
      }

      /*
       * Preserve:
       * - message ID
       * - role
       * - attachments
       *
       * Only replace the text.
       */
      const editedUserMessage: ChatMessage =
        {
          ...selectedMessage,
          content: trimmed,
        };

      /*
       * Keep everything before the
       * edited user message.
       *
       * Remove the old assistant response
       * and everything after it.
       */
      const historyBeforeEditedMessage =
        messages.slice(0, index);

      const assistantMessage: ChatMessage =
        {
          id: makeId(),
          role: "assistant",
          content: "",
          isStreaming: true,
        };

      const newHistory = [
        ...historyBeforeEditedMessage,
        editedUserMessage,
        assistantMessage,
      ];

      setMessages(newHistory);

      await generateResponse(
        [
          ...historyBeforeEditedMessage,
          editedUserMessage,
        ],
        assistantMessage.id,
      );
    },
    [
      messages,
      generateResponse,
      isStreaming,
    ],
  );

  /*
   * =========================================================
   * STOP STREAMING
   * =========================================================
   */
  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  /*
   * =========================================================
   * CLEAR CHAT
   * =========================================================
   *
   * Used by the "New chat" button.
   */
  const clearChat = useCallback(() => {
    /*
     * If a response is currently streaming,
     * stop it first.
     */
    abortRef.current?.abort();

    abortRef.current = null;

    setIsStreaming(false);
    setMessages([]);
  }, []);

  return {
    messages,
    isStreaming,

    sendMessage,
    retryMessage,
    editMessage,

    stopStreaming,
    clearChat,
  };
}