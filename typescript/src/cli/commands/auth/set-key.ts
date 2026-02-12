/**
 * @fileoverview `mirascope auth set-key` — store API key in local credentials.
 */

import { Args, Command, Options } from "@effect/cli";
import { Effect } from "effect";

import { writeCredentials } from "../../sdk/auth/config.js";

const apiKey = Args.text({ name: "api-key" }).pipe(
  Args.withDescription("Mirascope API key (starts with mk_)"),
);

const baseUrl = Options.text("base-url").pipe(
  Options.withDescription("API base URL (default: https://mirascope.com)"),
  Options.optional,
);

export const setKeyCommand = Command.make(
  "set-key",
  { apiKey, baseUrl },
  ({ apiKey, baseUrl }) =>
    Effect.gen(function* () {
      if (!apiKey.startsWith("mk_") && !apiKey.startsWith("mck_")) {
        yield* Effect.logError(
          'Invalid API key format. Keys should start with "mk_" or "mck_".',
        );
        return;
      }

      yield* writeCredentials({
        apiKey,
        baseUrl:
          baseUrl._tag === "Some" ? baseUrl.value : "https://mirascope.com",
      });

      yield* Effect.log("✓ API key saved.");
    }),
);
