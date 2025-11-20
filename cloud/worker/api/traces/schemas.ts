import { z } from "@hono/zod-openapi";

const KeyValueSchema = z
  .object({
    key: z.string(),
    value: z.object({
      stringValue: z.string().optional(),
      intValue: z.string().optional(),
      doubleValue: z.number().optional(),
      boolValue: z.boolean().optional(),
      arrayValue: z.any().optional(),
      kvlistValue: z.any().optional(),
    }),
  })
  .openapi("KeyValue");

const ResourceSchema = z
  .object({
    attributes: z.array(KeyValueSchema).optional(),
    droppedAttributesCount: z.number().optional(),
  })
  .openapi("Resource");

const SpanStatusSchema = z
  .object({
    code: z.number().optional(),
    message: z.string().optional(),
  })
  .openapi("SpanStatus");

const SpanSchema = z
  .object({
    traceId: z.string(),
    spanId: z.string(),
    parentSpanId: z.string().optional(),
    name: z.string(),
    kind: z.number().optional(),
    startTimeUnixNano: z.string(),
    endTimeUnixNano: z.string(),
    attributes: z.array(KeyValueSchema).optional(),
    droppedAttributesCount: z.number().optional(),
    events: z.array(z.any()).optional(),
    droppedEventsCount: z.number().optional(),
    status: SpanStatusSchema.optional(),
    links: z.array(z.any()).optional(),
    droppedLinksCount: z.number().optional(),
  })
  .openapi("Span");

const InstrumentationScopeSchema = z
  .object({
    name: z.string(),
    version: z.string().optional(),
    attributes: z.array(KeyValueSchema).optional(),
    droppedAttributesCount: z.number().optional(),
  })
  .openapi("InstrumentationScope");

const ScopeSpansSchema = z
  .object({
    scope: InstrumentationScopeSchema.optional(),
    spans: z.array(SpanSchema),
    schemaUrl: z.string().optional(),
  })
  .openapi("ScopeSpans");

const ResourceSpansSchema = z
  .object({
    resource: ResourceSchema.optional(),
    scopeSpans: z.array(ScopeSpansSchema),
    schemaUrl: z.string().optional(),
  })
  .openapi("ResourceSpans");

export const TraceRequestSchema = z
  .object({
    resourceSpans: z.array(ResourceSpansSchema),
  })
  .openapi("TraceRequest");

export const TraceResponseSchema = z
  .object({
    partialSuccess: z
      .object({
        rejectedSpans: z.number().optional(),
        errorMessage: z.string().optional(),
      })
      .optional(),
  })
  .openapi("TraceResponse");

export type KeyValue = z.infer<typeof KeyValueSchema>;
export type Resource = z.infer<typeof ResourceSchema>;
export type SpanStatus = z.infer<typeof SpanStatusSchema>;
export type Span = z.infer<typeof SpanSchema>;
export type InstrumentationScope = z.infer<typeof InstrumentationScopeSchema>;
export type ScopeSpans = z.infer<typeof ScopeSpansSchema>;
export type ResourceSpans = z.infer<typeof ResourceSpansSchema>;
export type TraceRequest = z.infer<typeof TraceRequestSchema>;
export type TraceResponse = z.infer<typeof TraceResponseSchema>;
