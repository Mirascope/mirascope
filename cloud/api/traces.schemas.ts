import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
  UnauthorizedError,
} from "@/errors";

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

export class TracesApi extends HttpApiGroup.make("traces").add(
  HttpApiEndpoint.post("create", "/traces")
    .setPayload(CreateTraceRequestSchema)
    .addSuccess(CreateTraceResponseSchema)
    .addError(UnauthorizedError, { status: UnauthorizedError.status })
    .addError(NotFoundError, { status: NotFoundError.status })
    .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
    .addError(DatabaseError, { status: DatabaseError.status })
    .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
) {}
