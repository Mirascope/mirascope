import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";
import { vi } from "vitest";

import type { ModelPricing } from "@/api/router/pricing";
import type { ProxyResult } from "@/api/router/proxy";
import type {
  RouterRequestContext,
  ValidatedRouterRequest,
} from "@/api/router/utils";
import type { PublicUser, EnvironmentApiKeyInfo } from "@/db/schema";

import { handleNonStreamingResponse } from "@/api/router/non-streaming";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

describe("Non-Streaming", () => {
  // Mock pricing data for tests (values in centi-cents per million tokens)
  // Using large values so small token counts still produce non-zero costs
  const mockPricing: ModelPricing = {
    input: 150_000_000n, // Very high to ensure non-zero cost with small token counts
    output: 600_000_000n, // Very high to ensure non-zero cost with small token counts
  };

  // Mock queue service for tests
  const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
    send: () => Effect.succeed(undefined),
  });

  describe("handleNonStreamingResponse", () => {
    it("handles response with usage data", async () => {
      const proxyResult: ProxyResult = {
        response: new Response(
          JSON.stringify({
            id: "1",
            choices: [{ message: { content: "Hello" } }],
            usage: { prompt_tokens: 10, completion_tokens: 5 },
          }),
          { status: 200 },
        ),
        body: {
          id: "1",
          choices: [{ message: { content: "Hello" } }],
          usage: { prompt_tokens: 10, completion_tokens: 5 },
        },
        isStreaming: false,
      };

      const context: RouterRequestContext = {
        routerRequestId: "req_test123",
        reservationId: "res_test123",
        request: {
          userId: "user_test",
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          routerRequestId: "req_test123",
          clawId: null,
        },
        modelPricing: mockPricing,
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
          accountType: "user",
          deletedAt: null,
        } satisfies PublicUser,
        apiKeyInfo: {
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          ownerId: "user_test",
          ownerName: "Test User",
          ownerEmail: "test@example.com",
          ownerAccountType: "user",
          ownerDeletedAt: null,
          clawId: null,
        } satisfies EnvironmentApiKeyInfo,
        provider: "openai",
        modelId: "gpt-4",
        parsedRequestBody: {},
      };

      const result = await Effect.runPromise(
        handleNonStreamingResponse(proxyResult, context, validated).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      expect(result).toBeInstanceOf(Response);
      expect(result.status).toBe(200);
    });

    it("handles response without usage data", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const proxyResult: ProxyResult = {
        response: new Response(
          JSON.stringify({
            id: "1",
            choices: [{ message: { content: "Hello" } }],
          }),
          { status: 200 },
        ),
        body: { id: "1", choices: [{ message: { content: "Hello" } }] },
        isStreaming: false,
      };

      const context: RouterRequestContext = {
        routerRequestId: "req_test123",
        reservationId: "res_test123",
        request: {
          userId: "user_test",
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          routerRequestId: "req_test123",
          clawId: null,
        },
        modelPricing: mockPricing,
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
          accountType: "user",
          deletedAt: null,
        } satisfies PublicUser,
        apiKeyInfo: {
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          ownerId: "user_test",
          ownerName: "Test User",
          ownerEmail: "test@example.com",
          ownerAccountType: "user",
          ownerDeletedAt: null,
          clawId: null,
        } satisfies EnvironmentApiKeyInfo,
        provider: "openai",
        modelId: "gpt-4",
        parsedRequestBody: {},
      };

      const result = await Effect.runPromise(
        handleNonStreamingResponse(proxyResult, context, validated).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      expect(result).toBeInstanceOf(Response);
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "[handleNonStreamingResponse] No usage data for request",
        ),
      );

      consoleWarnSpy.mockRestore();
    });

    it("handles queue enqueue failure gracefully", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const proxyResult: ProxyResult = {
        response: new Response(
          JSON.stringify({
            id: "1",
            choices: [{ message: { content: "Hello" } }],
            usage: { prompt_tokens: 10, completion_tokens: 5 },
          }),
          { status: 200 },
        ),
        body: {
          id: "1",
          choices: [{ message: { content: "Hello" } }],
          usage: { prompt_tokens: 10, completion_tokens: 5 },
        },
        isStreaming: false,
      };

      const context: RouterRequestContext = {
        routerRequestId: "req_test123",
        reservationId: "res_test123",
        request: {
          userId: "user_test",
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          routerRequestId: "req_test123",
          clawId: null,
        },
        modelPricing: mockPricing,
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
          accountType: "user",
          deletedAt: null,
        } satisfies PublicUser,
        apiKeyInfo: {
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          ownerId: "user_test",
          ownerName: "Test User",
          ownerEmail: "test@example.com",
          ownerAccountType: "user",
          ownerDeletedAt: null,
          clawId: null,
        } satisfies EnvironmentApiKeyInfo,
        provider: "openai",
        modelId: "gpt-4",
        parsedRequestBody: {},
      };

      // Create a failing queue layer
      const failingQueueLayer = Layer.succeed(RouterMeteringQueueService, {
        send: () => Effect.fail(new Error("Queue is down")),
      });

      const result = await Effect.runPromise(
        handleNonStreamingResponse(proxyResult, context, validated).pipe(
          Effect.provide(failingQueueLayer),
        ),
      );

      // Response should still be returned successfully
      expect(result).toBeInstanceOf(Response);
      expect(result.status).toBe(200);

      // Error should be logged
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "[handleNonStreamingResponse] Failed to enqueue metering",
        ),
        expect.anything(),
      );

      consoleErrorSpy.mockRestore();
    });

    it("handles response without body", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const proxyResult: ProxyResult = {
        response: new Response(null, { status: 204 }),
        body: null,
        isStreaming: false,
      };

      const context: RouterRequestContext = {
        routerRequestId: "req_test123",
        reservationId: "res_test123",
        request: {
          userId: "user_test",
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          routerRequestId: "req_test123",
          clawId: null,
        },
        modelPricing: mockPricing,
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
          accountType: "user",
          deletedAt: null,
        } satisfies PublicUser,
        apiKeyInfo: {
          organizationId: "org_test",
          projectId: "proj_test",
          environmentId: "env_test",
          apiKeyId: "key_test",
          ownerId: "user_test",
          ownerName: "Test User",
          ownerEmail: "test@example.com",
          ownerAccountType: "user",
          ownerDeletedAt: null,
          clawId: null,
        } satisfies EnvironmentApiKeyInfo,
        provider: "openai",
        modelId: "gpt-4",
        parsedRequestBody: {},
      };

      const result = await Effect.runPromise(
        handleNonStreamingResponse(proxyResult, context, validated).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      expect(result).toBeInstanceOf(Response);
      expect(result.status).toBe(204);
      expect(consoleWarnSpy).toHaveBeenCalled();

      consoleWarnSpy.mockRestore();
    });
  });
});
