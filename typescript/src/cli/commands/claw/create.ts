/**
 * @fileoverview `mirascope claw create <name>` — provision a new claw.
 */

import { Args, Command, Options } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

const name = Args.text({ name: "name" }).pipe(
  Args.withDescription("Claw slug (URL-safe name)"),
);

const instanceType = Options.text("instance-type").pipe(
  Options.withDescription("Instance type (default: standard-1)"),
  Options.withDefault("standard-1"),
);

export const createCommand = Command.make(
  "create",
  { name, instanceType },
  ({ name, instanceType }) =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      yield* Effect.log(`Creating claw ${name}...`);
      // org is resolved from API key automatically
      const claw = yield* api.create("", name, instanceType);
      yield* Effect.log(`✓ Claw created: ${claw.slug} (${claw.id})`);
      yield* Effect.log(`  Status: ${claw.status}`);
    }),
);
