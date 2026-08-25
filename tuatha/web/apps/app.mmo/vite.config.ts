// tuatha.web.apps.app.mmo.vite — the Vite config for the app entry.
import { defineConfig } from "vite";

export default defineConfig({
  server: { port: 3000, host: "0.0.0.0" },
  build: { target: "es2022", sourcemap: true },
  optimizeDeps: { exclude: ["duckdb"] },
});
