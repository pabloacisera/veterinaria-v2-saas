import { defineConfig } from "@playwright/test";

const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:5173";
const BACKEND_URL = process.env.PLAYWRIGHT_API_URL || "http://localhost:8000";

export default defineConfig({
  testDir: ".",
  timeout: 60_000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: FRONTEND_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
  ...(process.env.CI
    ? {}
    : {
        webServer: [
          {
            command: "cd ../backend && uvicorn src.main:app --host 0.0.0.0 --port 8000",
            port: 8000,
            url: `${BACKEND_URL}/api/v1/auth/register`,
            reuseExistingServer: true,
            timeout: 120_000,
          },
          {
            command: "cd ../frontend && npx vite --port 5173",
            port: 5173,
            url: FRONTEND_URL,
            reuseExistingServer: true,
            timeout: 120_000,
          },
        ],
      }),
});
