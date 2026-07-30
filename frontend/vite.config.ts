import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/access_role": {
        target: "http://localhost:8000",
        changeOrigin: true,
        bypass(req) {
          // No proxear navegación del browser (SPA routing) — solo API calls
          const accept = req.headers["accept"] || "";
          if (accept.includes("text/html")) {
            return req.url;
          }
        },
      },
    },
  },
});
