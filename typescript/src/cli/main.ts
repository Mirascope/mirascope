#!/usr/bin/env node
/**
 * @fileoverview CLI entry point for `mirascope`.
 */

import { Command } from "@effect/cli";
import { NodeContext, NodeRuntime } from "@effect/platform-node";
import { Effect, Layer } from "effect";

import { rootCommand } from "./commands/root.js";
import { AuthService } from "./sdk/auth/service.js";
import { ClawApi } from "./sdk/claw/service.js";
import { MirascopeHttp } from "./sdk/http/client.js";

// Compose the live layer stack
const LiveLayer = ClawApi.Live.pipe(
  Layer.provide(MirascopeHttp.Live),
  Layer.provide(AuthService.fromConfig()),
);

const run = Command.run(rootCommand, {
  name: "mirascope",
  version: "0.1.0",
});

run(process.argv).pipe(
  Effect.provide(LiveLayer),
  Effect.provide(NodeContext.layer),
  NodeRuntime.runMain,
);
