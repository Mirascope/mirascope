import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
  UnauthorizedError,
  ClickHouseError,
} from "@/errors";
import {
  AnalyticsSummaryRequestSchema,
  AnalyticsSummaryResponseSchema,
  SearchRequestSchema,
  SearchResponseSchema,
  TraceDetailResponseSchema,
} from "@/api/search.schemas";

export const KeyValueSchema = Schema.Struct({
  key: Schema.String,
  value: Schema.Struct({
    stringValue: Schema.optional(Schema.String),
    intValue: Schema.optional(Schema.String),
    doubleValue: Schema.optional(Schema.Number),
    boolValue: Schema.optional(Schema.Boolean),
    arrayValue: Schema.optional(
      Schema.Struct({
        values: Schema.Array(Schema.Any),
      }),
    ),
    kvlistValue: Schema.optional(
      Schema.Struct({
        values: Schema.Array(
          Schema.Struct({
            key: Schema.String,
            value: Schema.Any,
          }),
        ),
      }),
    ),
  }),
});

export type KeyValue = typeof KeyValueSchema.Type;

export const ResourceSchema = Schema.Struct({
  attributes: Schema.optional(Schema.Array(KeyValueSchema)),
  droppedAttributesCount: Schema.optional(Schema.Number),
});

export type Resource = typeof ResourceSchema.Type;

export const SpanStatusSchema = Schema.Struct({
  code: Schema.optional(Schema.Number),
  message: Schema.optional(Schema.String),
});

export type SpanStatus = typeof SpanStatusSchema.Type;

export const SpanSchema = Schema.Struct({
  traceId: Schema.String,
  spanId: Schema.String,
  parentSpanId: Schema.optional(Schema.NullOr(Schema.String)),
  name: Schema.String,
  kind: Schema.optional(Schema.Number),
  startTimeUnixNano: Schema.String,
  endTimeUnixNano: Schema.String,
  attributes: Schema.optional(Schema.Array(KeyValueSchema)),
  droppedAttributesCount: Schema.optional(Schema.Number),
  events: Schema.optional(Schema.Array(Schema.Unknown)),
  droppedEventsCount: Schema.optional(Schema.Number),
  status: Schema.optional(SpanStatusSchema),
  links: Schema.optional(Schema.Array(Schema.Unknown)),
  droppedLinksCount: Schema.optional(Schema.Number),
});

export type Span = typeof SpanSchema.Type;

export const InstrumentationScopeSchema = Schema.Struct({
  name: Schema.String,
  version: Schema.optional(Schema.String),
  attributes: Schema.optional(Schema.Array(KeyValueSchema)),
  droppedAttributesCount: Schema.optional(Schema.Number),
});

export type InstrumentationScope = typeof InstrumentationScopeSchema.Type;

export const ScopeSpansSchema = Schema.Struct({
  scope: Schema.optional(InstrumentationScopeSchema),
  spans: Schema.Array(SpanSchema),
  schemaUrl: Schema.optional(Schema.String),
});

export type ScopeSpans = typeof ScopeSpansSchema.Type;

export const ResourceSpansSchema = Schema.Struct({
  resource: Schema.optional(ResourceSchema),
  scopeSpans: Schema.Array(ScopeSpansSchema),
  schemaUrl: Schema.optional(Schema.String),
});

export type ResourceSpans = typeof ResourceSpansSchema.Type;

export const CreateTraceRequestSchema = Schema.Struct({
  resourceSpans: Schema.Array(ResourceSpansSchema),
});

export type CreateTraceRequest = typeof CreateTraceRequestSchema.Type;

export const CreateTraceResponseSchema = Schema.Struct({
  partialSuccess: Schema.optional(
    Schema.Struct({
      rejectedSpans: Schema.optional(Schema.Number),
      errorMessage: Schema.optional(Schema.String),
    }),
  ),
});

export type CreateTraceResponse = typeof CreateTraceResponseSchema.Type;

export const PublicTraceSchema = Schema.Struct({
  id: Schema.String,
  otelTraceId: Schema.String,
  environmentId: Schema.String,
  projectId: Schema.String,
  organizationId: Schema.String,
  serviceName: Schema.NullOr(Schema.String),
  serviceVersion: Schema.NullOr(Schema.String),
  resourceAttributes: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: Schema.Unknown }),
  ),
  createdAt: Schema.NullOr(Schema.String),
});

export type PublicTraceResponse = typeof PublicTraceSchema.Type;

export const ListByFunctionHashResponseSchema = Schema.Struct({
  traces: Schema.Array(PublicTraceSchema),
  total: Schema.Number,
});

export type ListByFunctionHashResponse =
  typeof ListByFunctionHashResponseSchema.Type;

export class TracesApi extends HttpApiGroup.make("traces")
  .add(
    HttpApiEndpoint.post("create", "/traces")
      .setPayload(CreateTraceRequestSchema)
      .addSuccess(CreateTraceResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
  )
  .add(
    HttpApiEndpoint.post("search", "/traces/search")
      .setPayload(SearchRequestSchema)
      .addSuccess(SearchResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      })
      .addError(ClickHouseError, { status: ClickHouseError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("getTraceDetail", "/traces/:traceId")
      .setPath(
        Schema.Struct({
          traceId: Schema.String,
        }),
      )
      .addSuccess(TraceDetailResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      })
      .addError(ClickHouseError, { status: ClickHouseError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("getAnalyticsSummary", "/traces/analytics")
      .setUrlParams(AnalyticsSummaryRequestSchema)
      .addSuccess(AnalyticsSummaryResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      })
      .addError(ClickHouseError, { status: ClickHouseError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("listByFunctionHash", "/traces/function/hash/:hash")
      .setPath(Schema.Struct({ hash: Schema.String }))
      .setUrlParams(
        Schema.Struct({
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListByFunctionHashResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(ClickHouseError, { status: ClickHouseError.status }),
  ) {}
