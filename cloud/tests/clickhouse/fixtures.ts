/**
 * @fileoverview Effect-native test fixtures for ClickHouse transform tests.
 */

import { Effect } from "effect";
import type { SpanTransformInput } from "@/clickhouse/transform";

// =============================================================================
// Fixtures
// =============================================================================

/** Default span fixture for transform testing. */
const TestTransformSpanFixtureData: SpanTransformInput["span"] = {
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
};

/** Default transform input fixture data. */
const TestTransformInputFixtureData: SpanTransformInput = {
  span: TestTransformSpanFixtureData,
  environmentId: "00000000-0000-0000-0000-000000000020",
  projectId: "00000000-0000-0000-0000-000000000030",
  organizationId: "00000000-0000-0000-0000-000000000040",
  receivedAt: new Date("2024-01-01T00:00:00.123Z").getTime(),
  serviceName: "svc",
  serviceVersion: "1.0.0",
  resourceAttributes: { region: "us-east-1" },
};

// =============================================================================
// Effect-native Fixtures
// =============================================================================

type SpanOverrides = Partial<SpanTransformInput["span"]>;
type InputOverrides = Omit<Partial<SpanTransformInput>, "span"> & {
  span?: SpanOverrides;
};

/**
 * Effect-native test fixture for transform span.
 *
 * Use `yield* TestTransformSpanFixture()` or `yield* TestTransformSpanFixture({ ...overrides })`.
 */
export const TestTransformSpanFixture = (
  overrides: SpanOverrides = {},
): Effect.Effect<SpanTransformInput["span"]> =>
  Effect.succeed({ ...TestTransformSpanFixtureData, ...overrides });

/**
 * Effect-native test fixture for transform input.
 *
 * Use `yield* TestTransformInputFixture()` or `yield* TestTransformInputFixture({ ...overrides })`.
 */
export const TestTransformInputFixture = (
  overrides: InputOverrides = {},
): Effect.Effect<SpanTransformInput> => {
  const { span: spanOverrides, ...inputOverrides } = overrides;
  return Effect.succeed({
    ...TestTransformInputFixtureData,
    ...inputOverrides,
    span: { ...TestTransformSpanFixtureData, ...spanOverrides },
  });
};
