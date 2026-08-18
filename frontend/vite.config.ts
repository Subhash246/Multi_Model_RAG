import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api requests to the FastAPI backend during development so the
// frontend can just call fetch("/api/v1/chat") with no CORS juggling.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
