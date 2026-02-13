/**
 * Bootstrap config fetcher.
 *
 * Fetches the OpenClawConfig for a claw from the Mirascope internal API
 * via the `env.MIRASCOPE_CLOUD` Cloudflare service binding (in-process
 * RPC — no network hop, no bearer token).
 *
 * There is no HTTP fallback. Local dev relies on unit tests with mocked
 * service bindings; integration testing happens on a deployed staging
 * environment.
 */

import { Data, Effect } from "effect";

import type { DispatchEnv, OpenClawDeployConfig } from "./types";

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

/** Bootstrap config fetch failed (network or non-OK response). */
export class BootstrapFetchError extends Data.TaggedError(
  "BootstrapFetchError",
)<{
  readonly clawId: string;
  readonly message: string;
  readonly cause?: unknown;
}> {}

/** Response JSON decode failed. */
export class BootstrapDecodeError extends Data.TaggedError(
  "BootstrapDecodeError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

/** Claw slug resolution failed. */
export class ClawResolutionError extends Data.TaggedError(
  "ClawResolutionError",
)<{
  readonly orgSlug: string;
  readonly clawSlug: string;
  readonly statusCode: number;
  readonly body: string;
}> {}

// ---------------------------------------------------------------------------
// Internal fetch via service binding
// ---------------------------------------------------------------------------

/**
 * Perform a fetch against the Mirascope internal API via service binding.
 *
 * Service binding requests use a synthetic origin (`https://internal`) since
 * the binding ignores the hostname and routes in-process.
 */
function internalFetch(
  env: DispatchEnv,
  path: string,
  init?: RequestInit,
): Promise<Response> {
  return env.MIRASCOPE_CLOUD.fetch(`https://internal${path}`, init);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Fetch the bootstrap config for a claw by its ID.
 */
export const fetchBootstrapConfig = (
  clawId: string,
  env: DispatchEnv,
): Effect.Effect<
  OpenClawDeployConfig,
  BootstrapFetchError | BootstrapDecodeError
> =>
  Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: () =>
        internalFetch(env, `/api/internal/claws/${clawId}/bootstrap`, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }),
      catch: (cause) =>
        new BootstrapFetchError({
          clawId,
          message: `Bootstrap fetch failed for claw ${clawId}`,
          cause,
        }),
    });

    if (!response.ok) {
      const body = yield* Effect.tryPromise({
        try: () => response.text(),
        catch: () =>
          new BootstrapFetchError({
            clawId,
            message: `Bootstrap fetch failed for claw ${clawId}: ${response.status} ${response.statusText}`,
          }),
      });
      return yield* new BootstrapFetchError({
        clawId,
        message: `Bootstrap config fetch failed for claw ${clawId}: ${response.status} ${response.statusText} — ${body}`,
      });
    }

    return yield* Effect.tryPromise({
      try: () => response.json() as Promise<OpenClawDeployConfig>,
      catch: (cause) =>
        new BootstrapDecodeError({
          message: `Failed to decode bootstrap config for claw ${clawId}`,
          cause,
        }),
    });
  });

/**
 * Resolve org/claw slugs to a clawId.
 *
 * Used by both the auth middleware (path-based routing) and legacy
 * host-based routing.
 */
export const resolveClawId = (
  orgSlug: string,
  clawSlug: string,
  env: DispatchEnv,
): Effect.Effect<
  { clawId: string; organizationId: string },
  ClawResolutionError
> =>
  Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: () =>
        internalFetch(
          env,
          `/api/internal/claws/resolve/${orgSlug}/${clawSlug}`,
          {
            method: "GET",
            headers: { "Content-Type": "application/json" },
          },
        ),
      catch: (cause) =>
        new ClawResolutionError({
          orgSlug,
          clawSlug,
          statusCode: 0,
          body: `Network error: ${cause}`,
        }),
    });

    if (!response.ok) {
      const body = yield* Effect.tryPromise({
        try: () => response.text(),
        catch: () =>
          new ClawResolutionError({
            orgSlug,
            clawSlug,
            statusCode: response.status,
            body: "(could not read body)",
          }),
      });
      return yield* new ClawResolutionError({
        orgSlug,
        clawSlug,
        statusCode: response.status,
        body,
      });
    }

    return yield* Effect.tryPromise({
      try: () =>
        response.json() as Promise<{
          clawId: string;
          organizationId: string;
        }>,
      catch: (cause) =>
        new ClawResolutionError({
          orgSlug,
          clawSlug,
          statusCode: response.status,
          body: `Failed to decode response: ${cause}`,
        }),
    });
  });

/**
 * Report claw status back to the Mirascope API.
 *
 * Fire-and-forget — logs errors but never fails.
 */
export const reportClawStatus = (
  clawId: string,
  status: {
    status: string;
    errorMessage?: string;
    startedAt?: string;
  },
  env: DispatchEnv,
): Effect.Effect<void> =>
  Effect.gen(function* () {
    const result = yield* Effect.tryPromise({
      try: () =>
        internalFetch(env, `/api/internal/claws/${clawId}/status`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(status),
        }),
      catch: (err) => err,
    }).pipe(Effect.either);

    if (result._tag === "Left") {
      console.error(`Status report error for claw ${clawId}:`, result.left);
      return;
    }

    if (!result.right.ok) {
      console.error(
        `Status report failed for claw ${clawId}: ${result.right.status} ${result.right.statusText}`,
      );
    }
  });
