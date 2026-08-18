import { motion } from "framer-motion";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-4">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-center gap-2.5"
      >
        {/* Signature mark: a soft gradient orb standing in for the fusion
            of text, voice, and document inputs into one assistant. */}
        <span className="h-6 w-6 rounded-full accent-gradient shadow-floating" />
        <span className="text-[15px] font-semibold tracking-tight">
          Multimodal <span className="accent-gradient-text">RAG</span>
        </span>
      </motion.div>
      <ThemeToggle />
    </header>
  );
}
