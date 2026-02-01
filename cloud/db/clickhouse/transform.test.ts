/**
 * @fileoverview Tests for ClickHouse span transform.
 */

import { describe, expect, it } from "@effect/vitest";
import { Effect } from "effect";

import {
  transformSpanForClickHouse,
  formatDateTime64,
} from "@/db/clickhouse/transform";
import { TestTransformInputFixture } from "@/tests/db/clickhouse/fixtures";

// =============================================================================
// Tests
// =============================================================================

describe("transformSpanForClickHouse", () => {
  it.effect("maps span fields and attributes into ClickHouse format", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture();

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
    }),
  );

  it.effect("returns null duration for negative durations", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          startTimeUnixNano: "1700000001000000000",
          endTimeUnixNano: "1700000000000000000",
        },
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
          new Date(
            Number(BigInt(input.span.endTimeUnixNano!) / BigInt(1000000)),
          ),
          9,
        ),
      );
    }),
  );

  it.effect("calculates total_tokens from input_tokens and output_tokens", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture();
      const row = transformSpanForClickHouse(input);

      // Default fixture has input_tokens=12, output_tokens=34
      expect(row.total_tokens).toBe(46);
    }),
  );

  it.effect("uses explicit gen_ai.usage.total_tokens when available", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          attributes: {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
            "gen_ai.usage.input_tokens": 10,
            "gen_ai.usage.output_tokens": 20,
            "gen_ai.usage.total_tokens": 100,
            "gen_ai.usage.cost": 0.01,
          },
        },
      });

      const row = transformSpanForClickHouse(input);

      // Explicit total_tokens should take precedence
      expect(row.total_tokens).toBe(100);
    }),
  );

  it.effect("returns null total_tokens when no token attributes exist", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          attributes: {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
          },
        },
      });

      const row = transformSpanForClickHouse(input);

      expect(row.total_tokens).toBeNull();
    }),
  );

  it.effect("calculates total_tokens with only input_tokens", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          attributes: {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
            "gen_ai.usage.input_tokens": 50,
          },
        },
      });

      const row = transformSpanForClickHouse(input);

      expect(row.total_tokens).toBe(50);
    }),
  );

  it.effect("calculates total_tokens with only output_tokens", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          attributes: {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
            "gen_ai.usage.output_tokens": 75,
          },
        },
      });

      const row = transformSpanForClickHouse(input);

      expect(row.total_tokens).toBe(75);
    }),
  );

  it.effect("handles string token values", () =>
    Effect.gen(function* () {
      const input = yield* TestTransformInputFixture({
        span: {
          attributes: {
            "gen_ai.request.model": "gpt-4",
            "gen_ai.system": "openai",
            "gen_ai.usage.input_tokens": "20",
            "gen_ai.usage.output_tokens": "30",
          },
        },
      });

      const row = transformSpanForClickHouse(input);

      expect(row.total_tokens).toBe(50);
    }),
  );
});
