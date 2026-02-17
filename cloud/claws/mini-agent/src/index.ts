/**
 * Mac Mini Agent — Entry point.
 *
 * Lightweight HTTP server for claw provisioning and management.
 * Runs on each Mac Mini under the `clawadmin` account.
 */
import { Hono } from "hono";
import { logger } from "hono/logger";

import { loadConfig } from "./lib/config.js";
import { authMiddleware } from "./middleware/auth.js";
import { clawRoutes } from "./routes/claws.js";
import { healthRoutes } from "./routes/health.js";

const config = loadConfig();
const app = new Hono();

// Logging
app.use("*", logger());

// Auth on all routes except health (health is useful for tunnel verification)
app.use("/claws/*", authMiddleware(config.authToken));
app.use("/claws", authMiddleware(config.authToken));

// Routes
app.route("/", healthRoutes(config));
app.route("/", clawRoutes(config));

// 404 handler
app.notFound((c) => c.json({ error: "Not found" }, 404));

// Error handler
app.onError((err, c) => {
  console.error(`[error] ${err.message}`, err.stack);
  return c.json({ error: "Internal server error", details: err.message }, 500);
});

console.log(`[mini-agent] Starting on port ${config.port}`);
console.log(`[mini-agent] Max claws: ${config.maxClaws}`);
console.log(
  `[mini-agent] Port range: ${config.portRangeStart}-${config.portRangeEnd}`,
);
console.log(`[mini-agent] Tunnel config: ${config.tunnelConfigPath}`);

export default {
  port: config.port,
  fetch: app.fetch,
};
