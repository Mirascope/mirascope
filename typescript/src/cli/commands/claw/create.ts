/**
 * @fileoverview `mirascope claw create <org> <name>` — provision a new claw.
 */

import { Args, Command, Options } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

const org = Args.text({ name: "org" }).pipe(
  Args.withDescription("Organization slug"),
);

const name = Args.text({ name: "name" }).pipe(
  Args.withDescription("Claw name"),
);

const instanceType = Options.text("instance-type").pipe(
  Options.withDescription("Instance type (default: standard)"),
  Options.withDefault("standard"),
);

export const createCommand = Command.make(
  "create",
  { org, name, instanceType },
  ({ org, name, instanceType }) =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      yield* Effect.log(`Creating claw ${org}/${name}...`);
      const claw = yield* api.create(org, name, instanceType);
      yield* Effect.log(
        `✓ Claw created: ${claw.organizationSlug}/${claw.slug} (${claw.id})`,
      );
      yield* Effect.log(`  Status: ${claw.status}`);
    }),
);
