/**
 * Mac Mini Agent — Entry point.
 *
 * Lightweight HTTP server for claw provisioning and management.
 * Runs on each Mac Mini under the `clawadmin` account.
 * Built with Effect HttpApi.
 */
import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Effect, Layer } from "effect";

import { MiniAgentApi } from "./api.js";
import { AgentConfigLive, AgentConfigService } from "./config.js";
import {
  AuthMiddlewareLive,
  ClawsGroupLive,
  HealthGroupLive,
} from "./handlers.js";
import { Exec, ExecLive } from "./services/exec.js";
import { Launchd, LaunchdLive } from "./services/launchd.js";
import { Monitoring, MonitoringLive } from "./services/monitoring.js";
import {
  Provisioning,
  ProvisioningLive,
} from "./services/provisioning.js";
import { System, SystemLive } from "./services/system.js";
import { Tunnel, TunnelLive } from "./services/tunnel.js";
import { UserManager, UserManagerLive } from "./services/user.js";

// ─── Service Layers ────────────────────────────────────────

const ExecLayer = Layer.effect(Exec, ExecLive);
const LaunchdLayer = Layer.effect(Launchd, LaunchdLive).pipe(
  Layer.provide(ExecLayer),
);
const TunnelLayer = Layer.effect(Tunnel, TunnelLive).pipe(
  Layer.provide(ExecLayer),
);
const MonitoringLayer = Layer.effect(Monitoring, MonitoringLive).pipe(
  Layer.provide(ExecLayer),
);
const SystemLayer = Layer.effect(System, SystemLive).pipe(
  Layer.provide(ExecLayer),
);
const UserManagerLayer = Layer.effect(UserManager, UserManagerLive).pipe(
  Layer.provide(ExecLayer),
);
const ProvisioningLayer = Layer.effect(Provisioning, ProvisioningLive).pipe(
  Layer.provide(
    Layer.mergeAll(
      ExecLayer,
      UserManagerLayer,
      LaunchdLayer,
      TunnelLayer,
      MonitoringLayer,
    ),
  ),
);

const ServicesLayer = Layer.mergeAll(
  ExecLayer,
  LaunchdLayer,
  TunnelLayer,
  MonitoringLayer,
  SystemLayer,
  UserManagerLayer,
  ProvisioningLayer,
);

// ─── API Layer ─────────────────────────────────────────────

const ApiLive = HttpApiBuilder.api(MiniAgentApi).pipe(
  Layer.provide(HealthGroupLive),
  Layer.provide(ClawsGroupLive),
  Layer.provide(AuthMiddlewareLive),
  Layer.provide(AgentConfigLive),
  Layer.provide(ServicesLayer),
);

// ─── Web Handler (Bun) ────────────────────────────────────

const { handler, dispose } = HttpApiBuilder.toWebHandler(
  Layer.mergeAll(ApiLive, HttpServer.layerContext),
);

// Read port from env for Bun's default export
const port = parseInt(process.env.MINI_AGENT_PORT ?? "7600", 10);

console.log(`[mini-agent] Starting on port ${port}`);

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("[mini-agent] Shutting down...");
  await dispose();
  process.exit(0);
});

export default {
  port,
  fetch: handler,
};
