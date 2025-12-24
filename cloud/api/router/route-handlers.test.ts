import {
  describe,
  expect,
  it,
  TestApiKeyFixture,
  TEST_DATABASE_URL,
  MockDrizzleORM,
} from "@/tests/db";
import { Effect, Layer } from "effect";
import { Database } from "@/db";
import { Payments } from "@/payments";
import {
  validateRouterRequest,
  createPendingRouterRequest,
  reserveRouterFunds,
  handleRouterRequestFailure,
  handleNonStreamingResponse,
  handleStreamingResponse,
  type ValidatedRouterRequest,
  type RouterRequestContext,
} from "@/api/router/route-handlers";
import { DefaultMockPayments, MockPayments } from "@/tests/payments";
import { InternalError, UnauthorizedError, DatabaseError } from "@/errors";
import type { ProxyResult } from "@/api/router/proxy";
import type { ResponseMetadata } from "@/api/router/streaming";
import { vi } from "vitest";

describe("Route Handlers", () => {
  describe("validateRouterRequest", () => {
    it.effect("validates openai provider and authenticates", () =>
      Effect.gen(function* () {
        const { owner, apiKey } = yield* TestApiKeyFixture;

        const request = new Request(
          "http://localhost/router/v0/openai/v1/chat/completions",
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey.key,
            },
            body: JSON.stringify({
              model: "gpt-4",
              messages: [{ role: "user", content: "Hello" }],
            }),
          },
        );

        const result = yield* validateRouterRequest(request, "openai");

        expect(result.provider).toBe("openai");
        expect(result.modelId).toBe("gpt-4");
        expect(result.user.id).toBe(owner.id);
        expect(result.apiKeyInfo.apiKeyId).toBe(apiKey.id);
      }),
    );

    it.effect("fails with InternalError for unsupported provider", () =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/test", {
          method: "POST",
        });

        const result = yield* validateRouterRequest(
          request,
          "unsupported",
        ).pipe(Effect.flip);

        expect(result).toBeInstanceOf(InternalError);
        expect(result.message).toContain("Unsupported provider");
      }),
    );

    it.effect("fails with UnauthorizedError when no API key", () =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/test", {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        });

        const result = yield* validateRouterRequest(request, "openai").pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(UnauthorizedError);
        expect(result.message).toContain("Authentication required");
      }),
    );

    it.effect("fails when authenticated via session (no API key info)", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create a session for the user
        const expiresAt = new Date(Date.now() + 1000 * 60 * 60); // 1 hour
        const session = yield* db.sessions.create({
          userId: owner.id,
          data: { userId: owner.id, expiresAt },
        });

        const request = new Request("http://localhost/test", {
          method: "POST",
          headers: {
            Cookie: `session=${session.id}`,
          },
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        });

        const result = yield* validateRouterRequest(request, "openai").pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(UnauthorizedError);
        expect(result.message).toContain("API key required for router access");
      }),
    );

    it.effect("fails when model ID extraction fails", () =>
      Effect.gen(function* () {
        const { apiKey } = yield* TestApiKeyFixture;

        const request = new Request(
          "http://localhost/router/v0/openai/v1/chat/completions",
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey.key,
            },
            body: JSON.stringify({
              // Missing model field
              messages: [{ role: "user", content: "Hello" }],
            }),
          },
        );

        const result = yield* validateRouterRequest(request, "openai").pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(InternalError);
        expect(result.message).toContain("Failed to extract model ID");
      }),
    );

    it.effect("fails when request body is not JSON", () =>
      Effect.gen(function* () {
        const { apiKey } = yield* TestApiKeyFixture;

        const request = new Request(
          "http://localhost/router/v0/openai/v1/chat/completions",
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey.key,
            },
            body: "not json",
          },
        );

        const result = yield* validateRouterRequest(request, "openai").pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(InternalError);
        // When body isn't valid JSON, model extraction fails first
        expect(result.message).toContain("Failed to extract model ID");
      }),
    );

    it.effect("handles error when reading request body fails", () =>
      Effect.gen(function* () {
        const { apiKey } = yield* TestApiKeyFixture;

        // Create a mock request where clone().text() throws
        const mockRequest = {
          url: "http://localhost/router/v0/openai/v1/chat/completions",
          method: "POST",
          headers: new Headers({
            "X-API-Key": apiKey.key,
          }),
          clone: () => ({
            text: () => Promise.reject(new Error("Read failed")),
          }),
        } as unknown as Request;

        const result = yield* validateRouterRequest(mockRequest, "openai").pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(InternalError);
        expect(result.message).toContain("Failed to extract model ID");
      }),
    );
  });

  describe("createPendingRouterRequest", () => {
    it.effect("creates a router request record", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const requestId = yield* createPendingRouterRequest(validated);

        expect(requestId).toBeDefined();
        expect(typeof requestId).toBe("string");
      }),
    );
  });

  describe("reserveRouterFunds", () => {
    it.effect("reserves funds for a request", () =>
      Effect.gen(function* () {
        const { owner, org, project, environment, apiKey } =
          yield* TestApiKeyFixture;

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const reservationId = yield* reserveRouterFunds(
          validated,
          "req_123",
          org.stripeCustomerId,
        );

        expect(reservationId).toBeDefined();
        expect(typeof reservationId).toBe("string");
      }).pipe(Effect.provide(DefaultMockPayments)),
    );
  });

  describe("handleRouterRequestFailure", () => {
    it.effect("updates request and releases funds on failure", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create a router request first
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        // Handle failure
        yield* handleRouterRequestFailure(
          routerRequest.id,
          reservationId,
          {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
          "Test error",
        );

        // Verify request was updated
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("failure");
        expect(updated.errorMessage).toBe("Test error");
      }).pipe(Effect.provide(DefaultMockPayments)),
    );
  });

  describe("handleStreamingResponse", () => {
    it.effect("processes streaming response", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        // Create streaming response
        const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\ndata: [DONE]\n\n`;
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode(sseData));
            controller.close();
          },
        });

        const proxyResult: ProxyResult = {
          response: new Response(stream, {
            headers: { "content-type": "text/event-stream" },
          }),
          body: null,
          isStreaming: true,
          streamFormat: "sse",
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const responseMetadata: ResponseMetadata = {
          status: 200,
          statusText: "OK",
          headers: new Headers({ "content-type": "text/event-stream" }),
        };

        const response = yield* handleStreamingResponse(
          proxyResult,
          context,
          validated,
          responseMetadata,
          TEST_DATABASE_URL,
          {
            apiKey: "sk_test_123",
            routerPriceId: "price_test123",
            routerMeterId: "meter_test123",
          },
        );

        expect(response).toBeDefined();
        expect(response.headers.get("content-type")).toBe("text/event-stream");

        // Read the stream to trigger metering
        const text = yield* Effect.tryPromise(() => response.text());
        expect(text).toBe(sseData);
      }).pipe(Effect.provide(DefaultMockPayments)),
    );
  });

  describe("handleNonStreamingResponse", () => {
    it.effect("processes non-streaming response with usage", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 10,
              completion_tokens: 5,
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was updated with usage
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("success");
        expect(updated.inputTokens).toBe(10n);
        expect(updated.outputTokens).toBe(5n);
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("handles response when cost calculation fails", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "unknown-model", // Model that will fail cost calculation
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 10,
              completion_tokens: 5,
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "unknown-model",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "unknown-model", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was marked as failure
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("failure");
        expect(updated.errorMessage).toContain("No usage data");
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("handles response with no usage data", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: null, // No usage data
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was marked as failure
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("failure");
        expect(updated.errorMessage).toContain("No usage data");
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("processes non-streaming response with cache tokens", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 100,
              completion_tokens: 50,
              prompt_tokens_details: {
                cached_tokens: 20,
              },
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was updated with cache token usage
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("success");
        expect(updated.inputTokens).toBe(100n);
        expect(updated.outputTokens).toBe(50n);
        expect(updated.cacheReadTokens).toBe(20n);
        expect(updated.cacheWriteTokens).toBeNull();
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("processes non-streaming response with zero input tokens", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 0,
              completion_tokens: 10,
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was updated with null input tokens but valid output tokens
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("success");
        expect(updated.inputTokens).toBeNull();
        expect(updated.outputTokens).toBe(10n);
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("processes non-streaming response with zero output tokens", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Reserve funds
        const payments = yield* Payments;
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 10,
              completion_tokens: 0,
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        );

        expect(response).toBeDefined();

        // Verify request was updated with valid input tokens but null output tokens
        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          );

        expect(updated.status).toBe("success");
        expect(updated.inputTokens).toBe(10n);
        expect(updated.outputTokens).toBeNull();
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect(
      "processes non-streaming response with cache write tokens (Anthropic)",
      () =>
        Effect.gen(function* () {
          const { owner, project, environment, apiKey } =
            yield* TestApiKeyFixture;
          const db = yield* Database;

          // Create router request
          const routerRequest =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: owner.id,
                organizationId: project.organizationId,
                projectId: project.id,
                environmentId: environment.id,
                apiKeyId: apiKey.id,
                data: {
                  provider: "anthropic",
                  model: "claude-3-5-sonnet-20241022",
                  status: "pending",
                },
              },
            );

          // Reserve funds
          const payments = yield* Payments;
          const reservationId = yield* payments.products.router.reserveFunds({
            stripeCustomerId: "cus_test",
            estimatedCostCenticents: 1000n,
            routerRequestId: routerRequest.id,
          });

          const proxyResult: ProxyResult = {
            response: new Response(JSON.stringify({ result: "test" })),
            body: {
              usage: {
                input_tokens: 100,
                output_tokens: 50,
                cache_creation_input_tokens: 25,
              },
            },
            isStreaming: false,
          };

          const validated: ValidatedRouterRequest = {
            provider: "anthropic",
            modelId: "claude-3-5-sonnet-20241022",
            user: owner,
            apiKeyInfo: {
              apiKeyId: apiKey.id,
              ownerId: owner.id,
              ownerEmail: owner.email,
              ownerName: owner.name,
              ownerDeletedAt: null,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
            },
            parsedRequestBody: {
              model: "claude-3-5-sonnet-20241022",
              messages: [],
            },
          };

          const context: RouterRequestContext = {
            routerRequestId: routerRequest.id,
            reservationId,
            request: {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: routerRequest.id,
            },
          };

          const response = yield* handleNonStreamingResponse(
            proxyResult,
            context,
            validated,
          );

          expect(response).toBeDefined();

          // Verify request was updated with cache write token usage
          const updated =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
              {
                userId: owner.id,
                organizationId: project.organizationId,
                projectId: project.id,
                environmentId: environment.id,
                apiKeyId: apiKey.id,
                routerRequestId: routerRequest.id,
              },
            );

          expect(updated.status).toBe("success");
          expect(updated.inputTokens).toBe(100n);
          expect(updated.outputTokens).toBe(50n);
          expect(updated.cacheReadTokens).toBeNull();
          expect(updated.cacheWriteTokens).toBe(25n);
        }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("handles error when settleFunds fails", () =>
      Effect.gen(function* () {
        const { owner, project, environment, apiKey } =
          yield* TestApiKeyFixture;
        const db = yield* Database;

        // Create router request
        const routerRequest =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: owner.id,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: apiKey.id,
              data: {
                provider: "openai",
                model: "gpt-4",
                status: "pending",
              },
            },
          );

        // Mock payments that fails on settleFunds
        const consoleErrorSpy = vi
          .spyOn(console, "error")
          .mockImplementation(() => {});
        const mockPayments = new MockPayments();
        const mockPaymentsLayer = mockPayments.build();

        // Get the payments instance and mock settleFunds to fail
        const payments = yield* Payments.pipe(
          Effect.provide(mockPaymentsLayer),
        );
        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_test",
          estimatedCostCenticents: 1000n,
          routerRequestId: routerRequest.id,
        });

        const proxyResult: ProxyResult = {
          response: new Response(JSON.stringify({ result: "test" })),
          body: {
            usage: {
              prompt_tokens: 10,
              completion_tokens: 5,
            },
          },
          isStreaming: false,
        };

        const validated: ValidatedRouterRequest = {
          provider: "openai",
          modelId: "gpt-4",
          user: owner,
          apiKeyInfo: {
            apiKeyId: apiKey.id,
            ownerId: owner.id,
            ownerEmail: owner.email,
            ownerName: owner.name,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const context: RouterRequestContext = {
          routerRequestId: routerRequest.id,
          reservationId,
          request: {
            userId: owner.id,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: apiKey.id,
            routerRequestId: routerRequest.id,
          },
        };

        // Create mock that fails on settleFunds by creating a fresh Payments layer
        // that has settleFunds return an error
        const failingPaymentsLayer = Layer.succeed(Payments, {
          ...payments,
          products: {
            router: {
              ...payments.products.router,
              settleFunds: () =>
                Effect.fail(new DatabaseError({ message: "Settle failed" })),
            },
          },
        } as never);

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(failingPaymentsLayer));

        expect(response).toBeDefined();
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("Failed to settle reservation"),
          expect.anything(),
        );

        consoleErrorSpy.mockRestore();
      }).pipe(Effect.provide(DefaultMockPayments)),
    );
  });

  describe("handleRouterRequestFailure error paths", () => {
    it.effect("handles error when database update fails", () =>
      Effect.gen(function* () {
        const consoleErrorSpy = vi
          .spyOn(console, "error")
          .mockImplementation(() => {});

        // Create mock database that fails on update
        const failingDbLayer = new MockDrizzleORM()
          .update(new Error("Update failed"))
          .select([]) // For releaseFunds lookup
          .update([]) // For releaseFunds update
          .build();

        const mockPaymentsLayer = DefaultMockPayments;

        yield* handleRouterRequestFailure(
          "req_123",
          "res_123",
          {
            userId: "user_123",
            organizationId: "org_123",
            projectId: "proj_123",
            environmentId: "env_123",
            apiKeyId: "key_123",
            routerRequestId: "req_123",
          },
          "Test error",
        ).pipe(
          Effect.provide(failingDbLayer),
          Effect.provide(mockPaymentsLayer),
        );

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("Failed to update router request"),
          expect.anything(),
        );

        consoleErrorSpy.mockRestore();
      }),
    );

    it.effect("handles error when releaseFunds fails", () =>
      Effect.gen(function* () {
        const consoleErrorSpy = vi
          .spyOn(console, "error")
          .mockImplementation(() => {});

        // Create mock database that succeeds on update
        const mockDbLayer = new MockDrizzleORM().update([]).build();

        // Create mock payments that fails on releaseFunds
        const failingPaymentsLayer = Layer.succeed(Payments, {
          products: {
            router: {
              releaseFunds: () =>
                Effect.fail(new DatabaseError({ message: "Release failed" })),
              reserveFunds: () => Effect.succeed("res_123"),
              settleFunds: () => Effect.succeed(undefined),
            },
          },
        } as never);

        yield* handleRouterRequestFailure(
          "req_123",
          "res_123",
          {
            userId: "user_123",
            organizationId: "org_123",
            projectId: "proj_123",
            environmentId: "env_123",
            apiKeyId: "key_123",
            routerRequestId: "req_123",
          },
          "Test error",
        ).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(failingPaymentsLayer),
        );

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("Failed to release reservation"),
          expect.anything(),
        );

        consoleErrorSpy.mockRestore();
      }),
    );
  });
});
