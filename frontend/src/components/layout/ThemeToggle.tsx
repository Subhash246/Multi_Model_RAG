import { AnimatePresence, motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle color theme"
      className="relative flex h-9 w-9 items-center justify-center rounded-full
                 border border-border-light dark:border-border-dark
                 bg-surface-light dark:bg-surface-dark
                 text-ink-light dark:text-ink-dark
                 hover:border-accent-from/50 transition-colors
                 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/60"
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={theme}
          initial={{ opacity: 0, rotate: -90, scale: 0.6 }}
          animate={{ opacity: 1, rotate: 0, scale: 1 }}
          exit={{ opacity: 0, rotate: 90, scale: 0.6 }}
          transition={{ duration: 0.25 }}
          className="flex items-center justify-center"
        >
          {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
        </motion.span>
      </AnimatePresence>
    </button>
  );
}
