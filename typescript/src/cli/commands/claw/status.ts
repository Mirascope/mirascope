/**
 * @fileoverview `mirascope claw status <id>` — show claw status.
 */

import { Args, Command } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

const id = Args.text({ name: "id" }).pipe(Args.withDescription("Claw ID"));

export const statusCommand = Command.make("status", { id }, ({ id }) =>
  Effect.gen(function* () {
    const api = yield* ClawApi;
    const detail = yield* api.status(id);

    yield* Effect.log(`Claw: ${detail.slug}`);
    yield* Effect.log(`  ID:         ${detail.id}`);
    yield* Effect.log(`  Status:     ${detail.status}`);
    yield* Effect.log(`  Instance:   ${detail.instanceType}`);
    if (detail.displayName) {
      yield* Effect.log(`  Name:       ${detail.displayName}`);
    }
    if (detail.lastError) {
      yield* Effect.log(`  Error:      ${detail.lastError}`);
    }
  }),
);
