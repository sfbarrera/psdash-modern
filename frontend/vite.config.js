import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El proxy reenvia /api al backend FastAPI durante el desarrollo,
// evitando problemas de CORS. En produccion, Nginx cumple ese rol.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
