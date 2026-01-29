import { Effect, Layer } from "effect";
import { describe, it, expect, vi } from "vitest";

import type { ProxyResult } from "@/api/router/proxy";
import type {
  RouterRequestContext,
  ValidatedRouterRequest,
} from "@/api/router/utils";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";

import { handleNonStreamingResponse } from "@/api/router/non-streaming";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

describe("Non-Streaming", () => {
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
        },
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
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
          ownerDeletedAt: null,
        } satisfies ApiKeyInfo,
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
        },
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
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
          ownerDeletedAt: null,
        } satisfies ApiKeyInfo,
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
          "[handleNonStreamingResponse] No usage data or cost calculation failed",
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
        },
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
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
          ownerDeletedAt: null,
        } satisfies ApiKeyInfo,
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
        },
      };

      const validated: ValidatedRouterRequest = {
        user: {
          id: "user_test",
          name: "Test User",
          email: "test@example.com",
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
          ownerDeletedAt: null,
        } satisfies ApiKeyInfo,
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
