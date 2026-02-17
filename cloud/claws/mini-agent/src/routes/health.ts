/**
 * GET /health — Mini health check endpoint.
 */
import { Hono } from "hono";

import type { AgentConfig } from "../lib/config.js";

import { errorMessage } from "../lib/errors.js";
import { listClawUsers } from "../services/provisioning.js";
import { getSystemStats } from "../services/system.js";
import { getRouteCount } from "../services/tunnel.js";

export function healthRoutes(config: AgentConfig): Hono {
  const app = new Hono();

  app.get("/health", async (c) => {
    try {
      const [stats, clawUsers, routeCount] = await Promise.all([
        getSystemStats(),
        listClawUsers(),
        getRouteCount(config.tunnelConfigPath).catch(() => 0),
      ]);

      return c.json({
        hostname: stats.hostname,
        uptime: stats.uptime,
        cpu: stats.cpu,
        memory: stats.memory,
        disk: stats.disk,
        loadAverage: stats.loadAverage,
        claws: {
          active: clawUsers.length,
          max: config.maxClaws,
        },
        tunnel: {
          status: "connected" as const, // TODO: check cloudflared actual status
          routes: routeCount,
        },
      });
    } catch (error: unknown) {
      return c.json(
        { error: "Failed to get health status", details: errorMessage(error) },
        500,
      );
    }
  });

  return app;
}
