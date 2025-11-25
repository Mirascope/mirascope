import { os } from "@orpc/server";
import { z } from "zod";

// Zod schemas for oRPC (using standard zod instead of @hono/zod-openapi)
const KeyValueSchema = z.object({
  key: z.string(),
  value: z.object({
    stringValue: z.string().optional(),
    intValue: z.string().optional(),
    doubleValue: z.number().optional(),
    boolValue: z.boolean().optional(),
    arrayValue: z
      .object({
        values: z.array(z.any()),
      })
      .optional(),
    kvlistValue: z
      .object({
        values: z.array(
          z.object({
            key: z.string(),
            value: z.any(),
          }),
        ),
      })
      .optional(),
  }),
});

const ResourceSchema = z.object({
  attributes: z.array(KeyValueSchema).optional(),
  droppedAttributesCount: z.number().optional(),
});

const SpanStatusSchema = z.object({
  code: z.number().optional(),
  message: z.string().optional(),
});

const SpanSchema = z.object({
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
});

const InstrumentationScopeSchema = z.object({
  name: z.string(),
  version: z.string().optional(),
  attributes: z.array(KeyValueSchema).optional(),
  droppedAttributesCount: z.number().optional(),
});

const ScopeSpansSchema = z.object({
  scope: InstrumentationScopeSchema.optional(),
  spans: z.array(SpanSchema),
  schemaUrl: z.string().optional(),
});

const ResourceSpansSchema = z.object({
  resource: ResourceSchema.optional(),
  scopeSpans: z.array(ScopeSpansSchema),
  schemaUrl: z.string().optional(),
});

const CreateTraceRequestSchema = z.object({
  resourceSpans: z.array(ResourceSpansSchema),
});

const CreateTraceResponseSchema = z.object({
  partialSuccess: z
    .object({
      rejectedSpans: z.number().optional(),
      errorMessage: z.string().optional(),
    })
    .optional(),
});

// Type exports
export type KeyValue = z.infer<typeof KeyValueSchema>;
export type Resource = z.infer<typeof ResourceSchema>;
export type SpanStatus = z.infer<typeof SpanStatusSchema>;
export type Span = z.infer<typeof SpanSchema>;
export type InstrumentationScope = z.infer<typeof InstrumentationScopeSchema>;
export type ScopeSpans = z.infer<typeof ScopeSpansSchema>;
export type ResourceSpans = z.infer<typeof ResourceSpansSchema>;
export type CreateTraceRequest = z.infer<typeof CreateTraceRequestSchema>;
export type CreateTraceResponse = z.infer<typeof CreateTraceResponseSchema>;

export const createTrace = os
  .route({ method: "POST", path: "/traces" })
  .input(CreateTraceRequestSchema)
  .output(CreateTraceResponseSchema)
  .handler(
    async ({
      input,
    }: {
      input: CreateTraceRequest;
    }): Promise<CreateTraceResponse> => {
      const serviceName =
        input.resourceSpans?.[0]?.resource?.attributes?.find(
          (attr) => attr.key === "service.name",
        )?.value?.stringValue || "unknown";

      let totalSpans = 0;
      input.resourceSpans?.forEach((rs) => {
        rs.scopeSpans?.forEach((ss) => {
          totalSpans += ss.spans?.length || 0;
        });
      });

      console.log(
        `[TRACE DEBUG] Received ${totalSpans} spans from service: ${serviceName}`,
      );
      console.log(
        "[TRACE DEBUG] Full trace data:",
        JSON.stringify(input, null, 2),
      );

      return { partialSuccess: {} };
    },
  );

export const router = os.tag("traces").router({
  create: createTrace,
});
