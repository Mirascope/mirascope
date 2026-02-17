/**
 * @fileoverview Mac Mini fleet management service.
 *
 * Handles fleet-level operations: finding available Mac Minis with capacity,
 * allocating ports, and making HTTP calls to the Mac Mini Agent API.
 */

import { eq, sql } from "drizzle-orm";
import { Schema } from "effect";
import { Context, Effect } from "effect";

import { DrizzleORM } from "@/db/client";
import { claws, macMinis } from "@/db/schema";

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export class FleetError extends Schema.TaggedError<FleetError>()(
  "FleetError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 503 as const;
}

export class AgentCallError extends Schema.TaggedError<AgentCallError>()(
  "AgentCallError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 502 as const;
}

// ---------------------------------------------------------------------------
// Service interface
// ---------------------------------------------------------------------------

export interface MacMiniFleetServiceInterface {
  /** Find an online Mac Mini with available capacity and allocate a port. */
  findAvailableMini(): Effect.Effect<
    {
      miniId: string;
      port: number;
      agentUrl: string;
      tunnelHostnameSuffix: string;
    },
    FleetError
  >;

  /** Make an HTTP call to a Mac Mini Agent. */
  callAgent(
    agentUrl: string,
    agentToken: string,
    method: string,
    path: string,
    body?: unknown,
  ): Effect.Effect<unknown, AgentCallError>;
}

export class MacMiniFleetService extends Context.Tag("MacMiniFleetService")<
  MacMiniFleetService,
  MacMiniFleetServiceInterface
>() {}

// ---------------------------------------------------------------------------
// Live implementation
// ---------------------------------------------------------------------------

export const LiveMacMiniFleetService = Effect.gen(function* () {
  const drizzle = yield* DrizzleORM;

  return {
    findAvailableMini: () =>
      Effect.gen(function* () {
        // Get all online minis with their current claw counts
        const minis = yield* drizzle
          .select({
            id: macMinis.id,
            agentUrl: macMinis.agentUrl,
            maxClaws: macMinis.maxClaws,
            portRangeStart: macMinis.portRangeStart,
            portRangeEnd: macMinis.portRangeEnd,
            tunnelHostnameSuffix: macMinis.tunnelHostnameSuffix,
            clawCount: sql<number>`count(${claws.id})::int`,
          })
          .from(macMinis)
          .leftJoin(claws, eq(claws.miniId, macMinis.id))
          .where(eq(macMinis.status, "online"))
          .groupBy(macMinis.id)
          .pipe(
            Effect.mapError(
              (e) =>
                new FleetError({
                  message: `Failed to query fleet: ${e}`,
                  cause: e,
                }),
            ),
          );

        // Find first mini with available capacity
        const available = minis.find((m) => m.clawCount < m.maxClaws);
        if (!available) {
          return yield* Effect.fail(
            new FleetError({
              message: "No Mac Minis available with capacity",
            }),
          );
        }

        // Find next available port on this mini
        const usedPorts = yield* drizzle
          .select({ port: claws.miniPort })
          .from(claws)
          .where(eq(claws.miniId, available.id))
          .pipe(
            Effect.mapError(
              (e) =>
                new FleetError({
                  message: `Failed to query used ports: ${e}`,
                  cause: e,
                }),
            ),
          );

        const usedPortSet = new Set(
          usedPorts.map((p) => p.port).filter((p): p is number => p != null),
        );

        let port: number | null = null;
        for (
          let p = available.portRangeStart;
          p <= available.portRangeEnd;
          p++
        ) {
          if (!usedPortSet.has(p)) {
            port = p;
            break;
          }
        }

        if (port == null) {
          return yield* Effect.fail(
            new FleetError({
              message: `No available ports on mini ${available.id}`,
            }),
          );
        }

        return {
          miniId: available.id,
          port,
          agentUrl: available.agentUrl,
          tunnelHostnameSuffix: available.tunnelHostnameSuffix,
        };
      }),

    callAgent: (
      agentUrl: string,
      agentToken: string,
      method: string,
      path: string,
      body?: unknown,
    ) =>
      Effect.gen(function* () {
        const url = `${agentUrl.replace(/\/$/, "")}${path}`;

        const response = yield* Effect.tryPromise({
          try: () =>
            fetch(url, {
              method,
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${agentToken}`,
              },
              body: body != null ? JSON.stringify(body) : undefined,
            }),
          catch: (cause) =>
            new AgentCallError({
              message: `Failed to reach agent at ${url}: ${cause instanceof Error ? cause.message : String(cause)}`,
              cause,
            }),
        });

        if (!response.ok) {
          const text = yield* Effect.tryPromise({
            try: () => response.text(),
            catch: () =>
              new AgentCallError({
                message: `Agent returned ${response.status} and body was unreadable`,
              }),
          });
          return yield* Effect.fail(
            new AgentCallError({
              message: `Agent returned ${response.status}: ${text}`,
            }),
          );
        }

        const json = yield* Effect.tryPromise({
          try: () => response.json(),
          catch: (cause) =>
            new AgentCallError({
              message: `Failed to parse agent response: ${cause instanceof Error ? cause.message : String(cause)}`,
              cause,
            }),
        });

        return json;
      }),
  } satisfies MacMiniFleetServiceInterface;
});
