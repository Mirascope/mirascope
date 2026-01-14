import { Effect } from "effect";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import { DrizzleORM } from "@/db/client";
import { organizations } from "@/db/schema";
import { eq } from "drizzle-orm";
import {
  SpansMeteringQueueService,
  type SpanMeteringMessage,
} from "@/workers/spansMeteringQueue";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
  ListByFunctionHashResponse,
} from "@/api/traces.schemas";
import type { PublicTrace } from "@/db/traces";

export * from "@/api/traces.schemas";

/**
 * Enqueues span metering messages for accepted spans.
 *
 * Fetches the organization's Stripe customer ID and enqueues a metering
 * message for each accepted span. Errors are logged but don't fail the
 * trace creation - eventual consistency via reconciliation is acceptable.
 *
 * @param spanIds - Array of accepted span IDs
 * @param organizationId - Organization ID
 * @param projectId - Project ID
 * @param environmentId - Environment ID
 * @returns Effect that completes when messages are enqueued
 */
function enqueueSpanMetering(
  spanIds: string[],
  organizationId: string,
  projectId: string,
  environmentId: string,
): Effect.Effect<void, never, DrizzleORM | SpansMeteringQueueService> {
  return Effect.gen(function* () {
    if (spanIds.length === 0) {
      return;
    }

    const client = yield* DrizzleORM;
    const queue = yield* SpansMeteringQueueService;

    // Fetch organization to get stripe customer ID
    const [org] = yield* client
      .select({ stripeCustomerId: organizations.stripeCustomerId })
      .from(organizations)
      .where(eq(organizations.id, organizationId))
      .pipe(
        Effect.catchAll((error) => {
          console.error(
            `[traces] Failed to fetch organization ${organizationId} for span metering:`,
            error,
          );
          return Effect.succeed([]);
        }),
      );

    if (!org) {
      console.error(
        `[traces] Organization ${organizationId} not found for span metering`,
      );
      return;
    }

    // Enqueue metering message for each accepted span
    for (const spanId of spanIds) {
      const message: SpanMeteringMessage = {
        spanId,
        organizationId,
        projectId,
        environmentId,
        stripeCustomerId: org.stripeCustomerId,
        timestamp: Date.now(),
      };

      yield* queue.send(message).pipe(
        Effect.catchAll((error) => {
          console.error(
            `[traces] Failed to enqueue span metering for span ${spanId}:`,
            error,
          );
          return Effect.succeed(undefined);
        }),
      );
    }
  });
}

/**
 * Handler for creating traces from OTLP trace data.
 * Accepts OpenTelemetry trace data and stores it in the database.
 */
export const createTraceHandler = (payload: CreateTraceRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const result = yield* db.organizations.projects.environments.traces.create({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      data: { resourceSpans: payload.resourceSpans },
    });

    // Enqueue metering for accepted spans (fire-and-forget, errors logged)
    yield* enqueueSpanMetering(
      result.acceptedSpanIds,
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
    );

    const response: CreateTraceResponse = {
      partialSuccess:
        result.rejectedSpans > 0
          ? {
              rejectedSpans: result.rejectedSpans,
              errorMessage: `${result.rejectedSpans} spans were rejected due to errors`,
            }
          : {},
    };

    return response;
  });

// Convert Date to ISO string for API response
export const toTrace = (trace: PublicTrace) => ({
  ...trace,
  createdAt: trace.createdAt?.toISOString() ?? null,
});

/**
 * Handler for listing traces by function version hash.
 * Queries traces containing spans with the specified mirascope.version.hash attribute.
 */
export const listByFunctionHashHandler = (
  hash: string,
  params: { limit?: number; offset?: number },
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const { traces, total } =
      yield* db.organizations.projects.environments.traces.findByFunctionHash({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        functionHash: hash,
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      });

    const response: ListByFunctionHashResponse = {
      traces: traces.map(toTrace),
      total,
    };

    return response;
  });
