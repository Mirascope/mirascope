/**
 * @fileoverview Mac Mini fleet management service.
 *
 * Handles fleet-level operations: finding available Minis, allocating ports,
 * and making authenticated HTTP requests to Mini agents.
 */

import { and, eq, sql } from "drizzle-orm";
import { Context, Effect, Layer } from "effect";

import { decryptSecrets } from "@/claws/crypto";
import { ClawDeploymentError } from "@/claws/deployment/errors";
import { DrizzleORM } from "@/db/client";
import { claws, macMinis } from "@/db/schema";
import { DatabaseError } from "@/errors";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AvailableMini {
  miniId: string;
  agentUrl: string;
  port: number;
  tunnelHostnameSuffix: string;
}

// ---------------------------------------------------------------------------
// Service interface
// ---------------------------------------------------------------------------

export interface MacMiniFleetServiceInterface {
  /** Find a Mini with available capacity and allocate a port. */
  readonly findAvailableMini: () => Effect.Effect<
    AvailableMini,
    ClawDeploymentError
  >;

  /** Make an authenticated HTTP request to a Mini's agent. */
  readonly callAgent: (
    miniId: string,
    method: string,
    path: string,
    body?: unknown,
  ) => Effect.Effect<unknown, ClawDeploymentError>;
}

export class MacMiniFleetService extends Context.Tag("MacMiniFleetService")<
  MacMiniFleetService,
  MacMiniFleetServiceInterface
>() {}

// ---------------------------------------------------------------------------
// Live implementation
// ---------------------------------------------------------------------------

export const LiveMacMiniFleetService = Layer.effect(
  MacMiniFleetService,
  Effect.gen(function* () {
    const drizzle = yield* DrizzleORM;

    return {
      findAvailableMini: () =>
        Effect.gen(function* () {
          // Find online minis with their claw counts
          const minisWithCounts = yield* drizzle
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
                  new ClawDeploymentError({
                    message: `Failed to query mac_minis: ${e}`,
                    cause: e,
                  }),
              ),
            );

          // Find a mini with capacity
          const available = minisWithCounts.find(
            (m) => m.clawCount < m.maxClaws,
          );
          if (!available) {
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: "No Mac Minis available with capacity",
              }),
            );
          }

          // Find allocated ports on this mini
          const allocatedPorts = yield* drizzle
            .select({ port: claws.miniPort })
            .from(claws)
            .where(
              and(eq(claws.miniId, available.id), sql`${claws.miniPort} IS NOT NULL`),
            )
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to query allocated ports: ${e}`,
                    cause: e,
                  }),
              ),
            );

          const usedPorts = new Set(
            allocatedPorts.map((p) => p.port).filter((p): p is number => p != null),
          );

          // Find first available port in range
          let port: number | null = null;
          for (let p = available.portRangeStart; p <= available.portRangeEnd; p++) {
            if (!usedPorts.has(p)) {
              port = p;
              break;
            }
          }

          if (port == null) {
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: `No available ports on Mini ${available.id}`,
              }),
            );
          }

          return {
            miniId: available.id,
            agentUrl: available.agentUrl,
            port,
            tunnelHostnameSuffix: available.tunnelHostnameSuffix,
          } satisfies AvailableMini;
        }),

      callAgent: (miniId: string, method: string, path: string, body?: unknown) =>
        Effect.gen(function* () {
          // Look up the mini
          const [mini] = yield* drizzle
            .select({
              agentUrl: macMinis.agentUrl,
              agentAuthTokenEncrypted: macMinis.agentAuthTokenEncrypted,
              agentAuthTokenKeyId: macMinis.agentAuthTokenKeyId,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up Mini ${miniId}: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: `Mac Mini ${miniId} not found`,
              }),
            );
          }

          // Decrypt auth token if present
          let authToken: string | undefined;
          if (mini.agentAuthTokenEncrypted && mini.agentAuthTokenKeyId) {
            const secrets = yield* decryptSecrets(
              mini.agentAuthTokenEncrypted,
              mini.agentAuthTokenKeyId,
            ).pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to decrypt agent auth token: ${e}`,
                    cause: e,
                  }),
              ),
            );
            authToken = secrets.token as string;
          }

          // Make HTTP request
          const url = `${mini.agentUrl.replace(/\/$/, "")}${path}`;
          const headers: Record<string, string> = {
            "Content-Type": "application/json",
          };
          if (authToken) {
            headers["Authorization"] = `Bearer ${authToken}`;
          }

          const response = yield* Effect.tryPromise({
            try: () =>
              fetch(url, {
                method,
                headers,
                body: body ? JSON.stringify(body) : undefined,
              }),
            catch: (e) =>
              new ClawDeploymentError({
                message: `Agent request failed: ${method} ${path}: ${e}`,
                cause: e,
              }),
          });

          if (!response.ok) {
            const text = yield* Effect.tryPromise({
              try: () => response.text(),
              catch: () =>
                new ClawDeploymentError({
                  message: `Failed to read agent error response`,
                }),
            });
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: `Agent returned ${response.status}: ${text}`,
              }),
            );
          }

          // Parse JSON response (or return null for 204)
          if (response.status === 204) return null;

          return yield* Effect.tryPromise({
            try: () => response.json(),
            catch: (e) =>
              new ClawDeploymentError({
                message: `Failed to parse agent response: ${e}`,
                cause: e,
              }),
          });
        }),
    };
  }),
);
