import { Effect } from "effect";
import {
  type KeyValue,
  type ResourceSpans,
  type ScopeSpans,
  type CreateTraceRequest,
  type CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (payload: CreateTraceRequest) =>
  Effect.gen(function* () {
    const serviceName =
      payload.resourceSpans?.[0]?.resource?.attributes?.find(
        (attr: KeyValue) => attr.key === "service.name",
      )?.value?.stringValue || "unknown";

    let totalSpans = 0;
    payload.resourceSpans?.forEach((rs: ResourceSpans) => {
      rs.scopeSpans?.forEach((ss: ScopeSpans) => {
        totalSpans += ss.spans?.length || 0;
      });
    });

    yield* Effect.log(
      `[TRACE DEBUG] Received ${totalSpans} spans from service: ${serviceName}`,
    );
    yield* Effect.log(
      `[TRACE DEBUG] Full trace data: ${JSON.stringify(payload, null, 2)}`,
    );

    const response: CreateTraceResponse = { partialSuccess: {} };
    return response;
  });
