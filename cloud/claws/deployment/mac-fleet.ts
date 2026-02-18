/**
 * @fileoverview Mac fleet management service.
 *
 * Handles fleet-level operations: finding available Macs with capacity,
 * allocating ports, and making HTTP calls to the Mac Agent API.
 */

import { eq, sql } from "drizzle-orm";
import { Schema } from "effect";
import { Context, Effect } from "effect";

import { DrizzleORM } from "@/db/client";
import { claws, fleetMacs } from "@/db/schema";

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

export interface MacFleetServiceInterface {
  /** Find an online Mac with available capacity and allocate a port. */
  findAvailableMac(): Effect.Effect<
    {
      macId: string;
      port: number;
      agentUrl: string;
      tunnelHostnameSuffix: string;
    },
    FleetError
  >;

  /** Make an HTTP call to a Mac Agent. */
  callAgent(
    agentUrl: string,
    agentToken: string,
    method: string,
    path: string,
    body?: unknown,
  ): Effect.Effect<unknown, AgentCallError>;
}

export class MacFleetService extends Context.Tag("MacFleetService")<
  MacFleetService,
  MacFleetServiceInterface
>() {}

// ---------------------------------------------------------------------------
// Live implementation
// ---------------------------------------------------------------------------

export const LiveMacFleetService = Effect.gen(function* () {
  const drizzle = yield* DrizzleORM;

  return {
    findAvailableMac: () =>
      Effect.gen(function* () {
        // Get all online macs with their current claw counts
        const macs = yield* drizzle
          .select({
            id: fleetMacs.id,
            agentUrl: fleetMacs.agentUrl,
            maxClaws: fleetMacs.maxClaws,
            portRangeStart: fleetMacs.portRangeStart,
            portRangeEnd: fleetMacs.portRangeEnd,
            tunnelHostnameSuffix: fleetMacs.tunnelHostnameSuffix,
            clawCount: sql<number>`count(${claws.id})::int`,
          })
          .from(fleetMacs)
          .leftJoin(claws, eq(claws.macId, fleetMacs.id))
          .where(eq(fleetMacs.status, "active"))
          .groupBy(fleetMacs.id)
          .pipe(
            Effect.mapError(
              (e) =>
                new FleetError({
                  message: `Failed to query fleet: ${e}`,
                  cause: e,
                }),
            ),
          );

        // Find first mac with available capacity
        const available = macs.find((m) => m.clawCount < m.maxClaws);
        if (!available) {
          return yield* Effect.fail(
            new FleetError({
              message: "No Macs available with capacity",
            }),
          );
        }

        // Find next available port on this mac
        const usedPorts = yield* drizzle
          .select({ port: claws.macPort })
          .from(claws)
          .where(eq(claws.macId, available.id))
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
              message: `No available ports on mac ${available.id}`,
            }),
          );
        }

        return {
          macId: available.id,
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
  } satisfies MacFleetServiceInterface;
});
