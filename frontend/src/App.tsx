import { useState } from "react";
import { motion } from "framer-motion";

import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";

import { ChatWindow } from "./components/chat/ChatWindow";
import { ChatInput } from "./components/chat/ChatInput";

import { useChat } from "./hooks/useChat";

export default function App() {
  const {
    messages,
    isStreaming,
    sendMessage,
    retryMessage,
    editMessage,
    stopStreaming,
    clearChat,
  } = useChat();

  const [isSidebarOpen, setIsSidebarOpen] =
    useState(true);

  /*
   * =========================================================
   * NEW CHAT
   * =========================================================
   */
  const startNewChat = () => {
    clearChat();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: 0.5,
        ease: "easeOut",
      }}
      className="flex h-screen"
    >
      {/* =====================================================
          SIDEBAR
      ===================================================== */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() =>
          setIsSidebarOpen(
            (open) => !open,
          )
        }
        onNewChat={startNewChat}
      />

      {/* =====================================================
          MAIN APPLICATION
      ===================================================== */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* HEADER */}
        <Header />

        {/* ===================================================
            CHAT WINDOW

            Retry and Edit callbacks are passed here.
        =================================================== */}
        <ChatWindow
          messages={messages}
          onRetry={retryMessage}
          onEdit={editMessage}
          disabled={isStreaming}
        />

        {/* ===================================================
            CHAT INPUT
        =================================================== */}
        <ChatInput
          onSend={sendMessage}
          isStreaming={isStreaming}
          onStop={stopStreaming}
        />
      </div>
    </motion.div>
  );
}