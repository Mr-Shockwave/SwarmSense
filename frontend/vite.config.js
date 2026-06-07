import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// TODO [Person 4]: confirm proxy targets match backend port (config BACKEND_PORT).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward API + CopilotKit runtime + WebSocket to the FastAPI backend.
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/mission": { target: "http://localhost:8000", changeOrigin: true },
      "/map": { target: "http://localhost:8000", changeOrigin: true },
      "/rovers": { target: "http://localhost:8000", changeOrigin: true },
      "/targets": { target: "http://localhost:8000", changeOrigin: true },
      "/ws": { target: "ws://localhost:8000", ws: true },
    },
  },
});
