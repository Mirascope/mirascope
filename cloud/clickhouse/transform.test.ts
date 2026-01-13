/**
 * @fileoverview Tests for ClickHouse span transform.
 */

import { describe, expect, it } from "vitest";
import {
  transformSpanForClickHouse,
  type SpanTransformInput,
} from "@/clickhouse/transform";

// =============================================================================
// Helpers
// =============================================================================

const formatDateTime64 = (date: Date, precision: number): string => {
  const iso = date.toISOString();
  const [datePart, timePart] = iso.split("T");
  const timeWithoutZone = timePart?.replace("Z", "") ?? "00:00:00.000";
  const [time, milliseconds = ""] = timeWithoutZone.split(".");
  const paddedFraction = milliseconds
    .padEnd(precision, "0")
    .slice(0, precision);
  return `${datePart} ${time}.${paddedFraction}`;
};

const buildSpan = (
  overrides: Partial<SpanTransformInput["span"]> = {},
): SpanTransformInput["span"] => ({
  traceId: "otel-trace-1",
  spanId: "otel-span-1",
  parentSpanId: null,
  name: "LLM.Call",
  kind: 1,
  startTimeUnixNano: "1700000000000000000",
  endTimeUnixNano: "1700000001000000000",
  attributes: {
    "gen_ai.request.model": "gpt-4",
    "gen_ai.system": "openai",
    "gen_ai.usage.input_tokens": 12,
    "gen_ai.usage.output_tokens": 34,
    "gen_ai.usage.cost": 0.01,
    "mirascope.function_id": "function-1",
    "mirascope.function_name": "summarize",
    "mirascope.function_version": "v1",
    "exception.type": "Error",
    "exception.message": "boom",
  },
  status: { code: 2, message: "ERROR" },
  events: [{ name: "event" }],
  links: [{ traceId: "link-trace" }],
  ...overrides,
});

const buildInput = (
  overrides: Partial<SpanTransformInput> = {},
): SpanTransformInput => ({
  span: buildSpan(),
  environmentId: "00000000-0000-0000-0000-000000000020",
  projectId: "00000000-0000-0000-0000-000000000030",
  organizationId: "00000000-0000-0000-0000-000000000040",
  receivedAt: new Date("2024-01-01T00:00:00.123Z").getTime(),
  serviceName: "svc",
  serviceVersion: "1.0.0",
  resourceAttributes: { region: "us-east-1" },
  ...overrides,
});

// =============================================================================
// Tests
// =============================================================================

describe("transformSpanForClickHouse", () => {
  it("maps span fields and attributes into ClickHouse format", () => {
    const input = buildInput();

    const row = transformSpanForClickHouse(input);

    expect(row.name_lower).toBe("llm.call");
    expect(row.duration_ms).toBe(1000);
    expect(row.model).toBe("gpt-4");
    expect(row.provider).toBe("openai");
    expect(row.input_tokens).toBe(12);
    expect(row.output_tokens).toBe(34);
    expect(row.cost_usd).toBe(0.01);
    expect(row.function_id).toBe("function-1");
    expect(row.function_name).toBe("summarize");
    expect(row.function_version).toBe("v1");
    expect(row.error_type).toBe("Error");
    expect(row.error_message).toBe("boom");
    expect(row.attributes).toBe(JSON.stringify(input.span.attributes));
    expect(row.events).toBe(JSON.stringify(input.span.events));
    expect(row.links).toBe(JSON.stringify(input.span.links));
    expect(row.resource_attributes).toBe(
      JSON.stringify(input.resourceAttributes),
    );
    expect(row.created_at).toBe(
      formatDateTime64(new Date(input.receivedAt), 3),
    );
    expect(row._version).toBeTypeOf("number");
  });

  it("returns null duration for negative durations", () => {
    const input = buildInput({
      span: buildSpan({
        startTimeUnixNano: "1700000001000000000",
        endTimeUnixNano: "1700000000000000000",
      }),
    });

    const row = transformSpanForClickHouse(input);

    expect(row.duration_ms).toBeNull();
    expect(row.start_time).toBe(
      formatDateTime64(
        new Date(
          Number(BigInt(input.span.startTimeUnixNano!) / BigInt(1000000)),
        ),
        9,
      ),
    );
    expect(row.end_time).toBe(
      formatDateTime64(
        new Date(Number(BigInt(input.span.endTimeUnixNano!) / BigInt(1000000))),
        9,
      ),
    );
  });
});
