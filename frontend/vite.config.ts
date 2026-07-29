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
          // Solo proxear requests con content-type JSON (API calls), no navegación del browser
          if (!req.headers["content-type"]?.includes("application/json")) {
            return req.url;
          }
        },
      },
    },
  },
});
