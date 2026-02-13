/**
 * @fileoverview `mirascope claw status <id>` — show claw status.
 */

import { Args, Command } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

const id = Args.text({ name: "id" }).pipe(
  Args.withDescription("Claw ID or org/name"),
);

export const statusCommand = Command.make("status", { id }, ({ id }) =>
  Effect.gen(function* () {
    const api = yield* ClawApi;
    const detail = yield* api.status(id);

    yield* Effect.log(`Claw: ${detail.organizationSlug}/${detail.slug}`);
    yield* Effect.log(`  ID:         ${detail.id}`);
    yield* Effect.log(`  Status:     ${detail.status}`);
    yield* Effect.log(`  Instance:   ${detail.instanceType}`);
    yield* Effect.log(`  Container:  ${detail.containerStatus ?? "unknown"}`);
    if (detail.uptime != null) {
      yield* Effect.log(`  Uptime:     ${Math.round(detail.uptime / 60)}m`);
    }
    if (detail.errorMessage) {
      yield* Effect.log(`  Error:      ${detail.errorMessage}`);
    }
  }),
);
