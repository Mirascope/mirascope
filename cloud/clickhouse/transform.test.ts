/**
 * @fileoverview Tests for ClickHouse span transform.
 */

import { describe, expect, it } from "@effect/vitest";
import { Effect } from "effect";
import {
  transformSpanForClickHouse,
  formatDateTime64,
} from "@/clickhouse/transform";
import { TestTransformInputFixture } from "@/tests/clickhouse/fixtures";

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
});
