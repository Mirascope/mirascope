/**
 * @fileoverview Credential file management for the Mirascope CLI.
 *
 * Reads/writes credentials from ~/.config/mirascope/credentials.json
 * with 0600 permissions for security.
 */

import { Effect, Schema } from "effect";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

import { AuthError } from "../errors.js";

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

export const CredentialsSchema = Schema.Struct({
  apiKey: Schema.String,
  baseUrl: Schema.optionalWith(Schema.String, {
    default: () => DEFAULT_BASE_URL,
  }),
});

export type Credentials = typeof CredentialsSchema.Type;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_BASE_URL = "https://mirascope.com";

const CONFIG_DIR = path.join(os.homedir(), ".config", "mirascope");
const CREDENTIALS_PATH = path.join(CONFIG_DIR, "credentials.json");

// ---------------------------------------------------------------------------
// Read / Write
// ---------------------------------------------------------------------------

export const readCredentials = (): Effect.Effect<Credentials, AuthError> =>
  Effect.gen(function* () {
    // Check env var override first
    const envKey = process.env.MIRASCOPE_API_KEY;
    if (envKey) {
      return {
        apiKey: envKey,
        baseUrl: process.env.MIRASCOPE_BASE_URL ?? DEFAULT_BASE_URL,
      };
    }

    // Read from file
    const raw = yield* Effect.try({
      try: () => fs.readFileSync(CREDENTIALS_PATH, "utf-8"),
      catch: () =>
        new AuthError({
          message: `No credentials found. Run \`mirascope auth set-key <key>\` or set MIRASCOPE_API_KEY.`,
        }),
    });

    const parsed = yield* Effect.try({
      try: () => JSON.parse(raw) as unknown,
      catch: () =>
        new AuthError({
          message: `Invalid credentials file at ${CREDENTIALS_PATH}`,
        }),
    });

    return yield* Schema.decodeUnknown(CredentialsSchema)(parsed).pipe(
      Effect.mapError(
        () =>
          new AuthError({
            message: `Malformed credentials file at ${CREDENTIALS_PATH}`,
          }),
      ),
    );
  });

export const writeCredentials = (
  creds: Credentials,
): Effect.Effect<void, AuthError> =>
  Effect.try({
    try: () => {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
      fs.writeFileSync(
        CREDENTIALS_PATH,
        JSON.stringify(creds, null, 2) + "\n",
        { mode: 0o600 },
      );
    },
    catch: (e) =>
      new AuthError({
        message: `Failed to write credentials: ${e instanceof Error ? e.message : String(e)}`,
      }),
  });

export const getCredentialsPath = () => CREDENTIALS_PATH;
