/**
 * @fileoverview `mirascope claw list` — list claws in the authenticated org.
 */

import { Command } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

export const listCommand = Command.make("list", {}, () =>
  Effect.gen(function* () {
    const api = yield* ClawApi;
    const claws = yield* api.list();

    if (claws.length === 0) {
      yield* Effect.log("No claws found.");
      return;
    }

    yield* Effect.log(`Found ${claws.length} claw(s):\n`);
    for (const claw of claws) {
      const name = claw.displayName ?? claw.slug;
      yield* Effect.log(
        `  ${claw.slug}  [${claw.status}]  ${claw.instanceType}  ${name}`,
      );
    }
  }),
);
