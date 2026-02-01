import { Effect } from "effect";
import assert from "node:assert";
import { vi, beforeEach } from "vitest";

import { clearPricingCache } from "@/api/router/pricing";
import { tokenCostHandler } from "@/api/token-cost.handlers";
import { PricingUnavailableError } from "@/errors";
import {
  describe,
  it,
  expect,
  createApiClient,
  TestApiContext,
} from "@/tests/api";
import { TEST_DATABASE_URL } from "@/tests/db";

describe("Token Cost Handler", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    clearPricingCache();

    // Mock pricing data fetch
    const mockData = {
      openai: {
        id: "openai",
        name: "OpenAI",
        models: {
          "gpt-4o": {
            id: "gpt-4o",
            name: "GPT-4o",
            cost: {
              input: 2.5, // $2.50 per 1M input tokens
              output: 10.0, // $10.00 per 1M output tokens
              cache_read: 1.25,
              cache_write: 3.125,
            },
          },
        },
      },
      anthropic: {
        id: "anthropic",
        name: "Anthropic",
        models: {
          "claude-sonnet-4-20250514": {
            id: "claude-sonnet-4-20250514",
            name: "Claude Sonnet 4",
            cost: {
              input: 3.0, // $3.00 per 1M input tokens
              output: 15.0, // $15.00 per 1M output tokens
              cache_read: 0.3,
              cache_write: 3.75, // 1.25x input price
            },
          },
        },
      },
      "google-ai-studio": {
        id: "google-ai-studio",
        name: "Google AI Studio",
        models: {
          "gemini-2.0-flash": {
            id: "gemini-2.0-flash",
            name: "Gemini 2.0 Flash",
            cost: {
              input: 0.1,
              output: 0.4,
            },
          },
        },
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData),
    }) as unknown as typeof fetch;
  });

  describe("calculate", () => {
    it.effect("calculates cost for valid OpenAI request", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 1000000, // 1M tokens
            outputTokens: 500000, // 500K tokens
          },
        });

        // 1M input tokens @ $2.50/1M = $2.50 = 25000 centicents
        // 500K output tokens @ $10.00/1M = $5.00 = 50000 centicents
        // Total = $7.50 = 75000 centicents
        expect(result.inputCostCenticents).toBe(25000);
        expect(result.outputCostCenticents).toBe(50000);
        expect(result.totalCostCenticents).toBe(75000);

        // Verify dollar amounts
        expect(result.inputCostDollars).toBe(2.5);
        expect(result.outputCostDollars).toBe(5.0);
        expect(result.totalCostDollars).toBe(7.5);

        // Cache costs should be undefined when not provided
        expect(result.cacheReadCostCenticents).toBeUndefined();
        expect(result.cacheWriteCostCenticents).toBeUndefined();
      }),
    );

    it.effect("calculates cost with cache tokens for Anthropic", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "anthropic",
          model: "claude-sonnet-4-20250514",
          usage: {
            inputTokens: 1000000, // 1M tokens
            outputTokens: 500000, // 500K tokens
            cacheReadTokens: 200000, // 200K cache read tokens
            cacheWriteTokens: 100000, // 100K cache write tokens
            cacheWriteBreakdown: { ephemeral5m: 100000, ephemeral1h: 0 },
          },
        });

        // 1M input tokens @ $3.00/1M = $3.00 = 30000 centicents
        // 500K output tokens @ $15.00/1M = $7.50 = 75000 centicents
        // 200K cache read @ $0.30/1M = $0.06 = 600 centicents
        // 100K cache write (5m ephemeral) @ $3.75/1M = $0.375 = 3750 centicents
        expect(result.inputCostCenticents).toBe(30000);
        expect(result.outputCostCenticents).toBe(75000);
        expect(result.cacheReadCostCenticents).toBe(600);
        expect(result.cacheWriteCostCenticents).toBe(3750);

        // Total = 30000 + 75000 + 600 + 3750 = 109350
        expect(result.totalCostCenticents).toBe(109350);
      }),
    );

    it.effect("calculates cost for Google provider", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "google",
          model: "gemini-2.0-flash",
          usage: {
            inputTokens: 1000000,
            outputTokens: 1000000,
          },
        });

        // 1M input tokens @ $0.10/1M = $0.10 = 1000 centicents
        // 1M output tokens @ $0.40/1M = $0.40 = 4000 centicents
        expect(result.inputCostCenticents).toBe(1000);
        expect(result.outputCostCenticents).toBe(4000);
        expect(result.totalCostCenticents).toBe(5000);
        expect(result.totalCostDollars).toBe(0.5);
      }),
    );

    it.effect("returns PricingUnavailableError for unknown model", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "nonexistent-model",
          usage: {
            inputTokens: 100,
            outputTokens: 50,
          },
        }).pipe(Effect.flip);

        assert(result instanceof PricingUnavailableError);
        expect(result._tag).toBe("PricingUnavailableError");
        expect(result.message).toContain("openai/nonexistent-model");
        expect(result.provider).toBe("openai");
        expect(result.model).toBe("nonexistent-model");
      }),
    );

    it.effect("returns helpful error for unsupported provider", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "azure",
          model: "gpt-4",
          usage: {
            inputTokens: 100,
            outputTokens: 50,
          },
        }).pipe(Effect.flip);

        assert(result instanceof PricingUnavailableError);
        expect(result._tag).toBe("PricingUnavailableError");
        expect(result.message).toContain("Provider 'azure' is not supported");
        expect(result.message).toContain("anthropic, google, openai");
        expect(result.message).toContain(
          "github.com/Mirascope/mirascope/issues",
        );
        expect(result.provider).toBe("azure");
      }),
    );

    it.effect("handles zero tokens correctly", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 0,
            outputTokens: 0,
          },
        });

        expect(result.inputCostCenticents).toBe(0);
        expect(result.outputCostCenticents).toBe(0);
        expect(result.totalCostCenticents).toBe(0);
        expect(result.totalCostDollars).toBe(0);
      }),
    );

    it.effect("handles small token counts accurately", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 100, // Small number
            outputTokens: 50,
          },
        });

        // 100 input tokens @ $2.50/1M = (100 * 25000) / 1000000 = 2 centicents
        // 50 output tokens @ $10.00/1M = (50 * 100000) / 1000000 = 5 centicents
        expect(result.inputCostCenticents).toBe(2);
        expect(result.outputCostCenticents).toBe(5);
        expect(result.totalCostCenticents).toBe(7);
      }),
    );

    it.effect("applies 5% router fee when viaRouter is true", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 1000000, // 1M tokens
            outputTokens: 500000, // 500K tokens
          },
          viaRouter: true,
        });

        // Base costs:
        // 1M input tokens @ $2.50/1M = 25000 centicents
        // 500K output tokens @ $10.00/1M = 50000 centicents
        // Total = 75000 centicents
        //
        // With 5% router fee (rounded up):
        // Input: ceil(25000 * 1.05) = 26250
        // Output: ceil(50000 * 1.05) = 52500
        // Total: ceil(75000 * 1.05) = 78750
        expect(result.inputCostCenticents).toBe(26250);
        expect(result.outputCostCenticents).toBe(52500);
        expect(result.totalCostCenticents).toBe(78750);
      }),
    );

    it.effect("does not apply router fee when viaRouter is false", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 1000000,
            outputTokens: 500000,
          },
          viaRouter: false,
        });

        // No router fee - same as base costs
        expect(result.inputCostCenticents).toBe(25000);
        expect(result.outputCostCenticents).toBe(50000);
        expect(result.totalCostCenticents).toBe(75000);
      }),
    );

    it.effect("does not apply router fee when viaRouter is undefined", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "openai",
          model: "gpt-4o",
          usage: {
            inputTokens: 1000000,
            outputTokens: 500000,
          },
          // viaRouter not specified
        });

        // No router fee - same as base costs
        expect(result.inputCostCenticents).toBe(25000);
        expect(result.outputCostCenticents).toBe(50000);
        expect(result.totalCostCenticents).toBe(75000);
      }),
    );

    it.effect("applies router fee to cache costs as well", () =>
      Effect.gen(function* () {
        const result = yield* tokenCostHandler({
          provider: "anthropic",
          model: "claude-sonnet-4-20250514",
          usage: {
            inputTokens: 1000000,
            outputTokens: 500000,
            cacheReadTokens: 200000,
            cacheWriteTokens: 100000,
            cacheWriteBreakdown: { ephemeral5m: 100000, ephemeral1h: 0 },
          },
          viaRouter: true,
        });

        // Base costs:
        // Input: 30000, Output: 75000, CacheRead: 600, CacheWrite: 3750
        // Total: 109350
        //
        // With 5% router fee (rounded up):
        expect(result.inputCostCenticents).toBe(Math.ceil(30000 * 1.05)); // 31500
        expect(result.outputCostCenticents).toBe(Math.ceil(75000 * 1.05)); // 78750
        expect(result.cacheReadCostCenticents).toBe(Math.ceil(600 * 1.05)); // 630
        expect(result.cacheWriteCostCenticents).toBe(Math.ceil(3750 * 1.05)); // 3938
        expect(result.totalCostCenticents).toBe(Math.ceil(109350 * 1.05)); // 114818
      }),
    );
  });
});

// ============================================================================
// Router Integration Tests
// ============================================================================
// These tests exercise the full HTTP flow through the router, including
// API key authentication (covers router.ts lines 461-464).

describe.sequential("Token Cost API", (it) => {
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;

  it.effect("setup API key client for token-cost tests", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;

      // Clear pricing cache and setup mock for router tests
      clearPricingCache();
      const mockPricingData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o": {
              id: "gpt-4o",
              name: "GPT-4o",
              cost: {
                input: 2.5,
                output: 10.0,
              },
            },
          },
        },
      };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockPricingData),
      }) as unknown as typeof fetch;

      const apiKeyInfo = {
        apiKeyId: "test-api-key-id",
        organizationId: org.id,
        projectId: "test-project-id",
        environmentId: "test-environment-id",
        ownerId: owner.id,
        ownerEmail: owner.email,
        ownerName: owner.name,
        ownerDeletedAt: owner.deletedAt,
      };

      const result = yield* Effect.promise(() =>
        createApiClient(
          TEST_DATABASE_URL,
          owner,
          apiKeyInfo,
          () => Effect.void,
        ),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect(
    "POST /token-cost - calculates cost with API key authentication",
    () =>
      Effect.gen(function* () {
        const result = yield* apiKeyClient["token-cost"].calculate({
          payload: {
            provider: "openai",
            model: "gpt-4o",
            usage: {
              inputTokens: 1000000,
              outputTokens: 500000,
            },
          },
        });

        // 1M input tokens @ $2.50/1M = 25000 centicents
        // 500K output tokens @ $10.00/1M = 50000 centicents
        expect(result.inputCostCenticents).toBe(25000);
        expect(result.outputCostCenticents).toBe(50000);
        expect(result.totalCostCenticents).toBe(75000);
      }),
  );

  it.effect("cleanup API key client", () =>
    Effect.gen(function* () {
      if (disposeApiKeyClient) {
        yield* Effect.promise(() => disposeApiKeyClient!());
      }
    }),
  );
});
