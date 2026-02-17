/**
 * Mac Mini Agent — Entry point.
 *
 * Lightweight HTTP server for claw provisioning and management.
 * Runs on each Mac Mini under the `clawadmin` account.
 *
 * Reimplemented with Effect HttpApi for strict typing and consistency
 * with the Mirascope Cloud codebase.
 */
import { HttpApiBuilder, HttpMiddleware } from "@effect/platform";
import { BunHttpServer, BunRuntime } from "@effect/platform-bun";
import { Layer } from "effect";

import { MiniAgentApi } from "./api.js";
import { ConfigLive } from "./Config.js";
import { ExecLive } from "./Exec.js";
import {
  AuthMiddlewareLive,
  ClawsHandlers,
  HealthHandlers,
} from "./handlers.js";
import { LaunchdLive } from "./services/Launchd.js";
import { MonitoringLive } from "./services/Monitoring.js";
import { ProvisioningLive } from "./services/Provisioning.js";
import { SystemLive } from "./services/System.js";
import { TunnelLive } from "./services/Tunnel.js";
import { UserManagerLive } from "./services/UserManager.js";

// All service layers
const ServicesLive = Layer.mergeAll(
  LaunchdLive,
  MonitoringLive,
  ProvisioningLive,
  SystemLive,
  TunnelLive,
  UserManagerLive,
).pipe(Layer.provide(ExecLive), Layer.provide(ConfigLive));

// Build the HTTP app from the API definition and handlers
const ApiLive = HttpApiBuilder.api(MiniAgentApi).pipe(
  Layer.provide(HealthHandlers),
  Layer.provide(ClawsHandlers),
  Layer.provide(AuthMiddlewareLive),
  Layer.provide(ServicesLive),
  Layer.provide(ConfigLive),
);

const port = parseInt(process.env.AGENT_PORT ?? "7600", 10);

console.log(`[mini-agent] Starting on port ${port}`);

// Start the server
const ServerLive = HttpApiBuilder.serve(HttpMiddleware.logger).pipe(
  Layer.provide(ApiLive),
  Layer.provide(BunHttpServer.layer({ port })),
);

BunRuntime.runMain(Layer.launch(ServerLive));
