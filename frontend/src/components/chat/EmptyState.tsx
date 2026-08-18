import { motion } from "framer-motion";

export function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="flex h-full flex-col items-center justify-center gap-4 text-center px-6"
    >
      <span className="h-12 w-12 rounded-full accent-gradient shadow-floating" />
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Ask anything. Attach a doc, or just talk.
        </h1>
        <p className="mt-2 max-w-md text-sm text-muted-light dark:text-muted-dark">
          Upload documents, drop in audio, or type a question — everything
          becomes context for the same conversation.
        </p>
      </div>
    </motion.div>
  );
}
