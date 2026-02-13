/**
 * @fileoverview `mirascope claw delete <id>` — delete a claw.
 */

import { Args, Command, Options } from "@effect/cli";
import { Effect } from "effect";

import { ClawApi } from "../../sdk/claw/service.js";

const id = Args.text({ name: "id" }).pipe(
  Args.withDescription("Claw ID (always explicit, never uses active claw)"),
);

const force = Options.boolean("force").pipe(
  Options.withDescription("Skip confirmation prompt"),
  Options.withDefault(false),
);

export const deleteCommand = Command.make(
  "delete",
  { id, force },
  ({ id, force }) =>
    Effect.gen(function* () {
      const api = yield* ClawApi;

      if (!force) {
        // TODO: interactive confirmation prompt
        yield* Effect.log(
          `⚠  This will permanently delete claw ${id} and all its data.`,
        );
        yield* Effect.log(`   Use --force to skip this warning.`);
        return;
      }

      yield* api.delete(id);
      yield* Effect.log(`✓ Claw ${id} deleted.`);
    }),
);
