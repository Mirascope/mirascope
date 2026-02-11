import { Effect, Layer } from "effect";
import { vi } from "vitest";

import type { ModelPricing } from "@/api/router/pricing";
import type { ProxyResult } from "@/api/router/proxy";
import type { ResponseMetadata } from "@/api/router/streaming";

// Mock pricing data for tests (values in centi-cents per million tokens)
const mockPricing: ModelPricing = {
  input: 1500n, // $0.15 per million tokens
  output: 6000n, // $0.60 per million tokens
};

import { handleNonStreamingResponse } from "@/api/router/non-streaming";
import { handleStreamingResponse } from "@/api/router/streaming";
import {
  validateRouterRequest,
  createPendingRouterRequest,
  reserveRouterFunds,
  handleRouterRequestFailure,
  enqueueRouterMetering,
  type ValidatedRouterRequest,
  type RouterRequestContext,
  type RouterRequestIdentifiers,
} from "@/api/router/utils";
import { Database } from "@/db/database";
import { InternalError, UnauthorizedError, DatabaseError } from "@/errors";
import { Payments } from "@/payments";
import {
  describe,
  expect,
  it,
  TestApiKeyFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { DefaultMockPayments, MockPayments } from "@/tests/payments";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

describe("Route Handlers", () => {
  describe("validateRouterRequest", () => {
    it.effect("validates openai provider and authenticates", () =>
      Effect.gen(function* () {
        const { owner, apiKey } = yield* TestApiKeyFixture;

        const request = new Request(
          "http://localhost/router/v2/openai/v1/chat/completions",
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
          "http://localhost/router/v2/openai/v1/chat/completions",
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
          "http://localhost/router/v2/openai/v1/chat/completions",
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
          url: "http://localhost/router/v2/openai/v1/chat/completions",
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
          },
          parsedRequestBody: { model: "gpt-4", messages: [] },
        };

        const result = yield* reserveRouterFunds(
          validated,
          "req_123",
          org.stripeCustomerId,
        );

        expect(result.reservationId).toBeDefined();
        expect(typeof result.reservationId).toBe("string");
        expect(result.modelPricing).toBeDefined();
        expect(typeof result.modelPricing.input).toBe("bigint");
        expect(typeof result.modelPricing.output).toBe("bigint");
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
            clawId: null,
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        const responseMetadata: ResponseMetadata = {
          status: 200,
          statusText: "OK",
          headers: new Headers({ "content-type": "text/event-stream" }),
        };

        // Mock queue service
        const mockQueueSendEffect = Effect.succeed(undefined);
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => mockQueueSendEffect,
        });

        const response = yield* handleStreamingResponse(
          proxyResult,
          context,
          validated,
          responseMetadata,
        ).pipe(Effect.provide(mockQueueLayer));

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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we don't expect immediate DB updates in this test
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we dont expect immediate DB updates in this test
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we dont expect immediate DB updates in this test
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we dont expect immediate DB updates in this test
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we dont expect immediate DB updates in this test
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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue,
        // so we dont expect immediate DB updates in this test
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
              ownerAccountType: "user" as const,
              ownerDeletedAt: null,
              organizationId: project.organizationId,
              projectId: project.id,
              environmentId: environment.id,
              clawId: null,
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
              clawId: null,
            },
            modelPricing: mockPricing,
          };

          // Mock queue service
          const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
            send: () => Effect.succeed(undefined),
          });

          const response = yield* handleNonStreamingResponse(
            proxyResult,
            context,
            validated,
          ).pipe(Effect.provide(mockQueueLayer));

          expect(response).toBeDefined();
          // Note: Metering now happens asynchronously via queue,
          // so we don't expect immediate DB updates in this test
        }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("handles response and enqueues successfully", () =>
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

        const mockPayments = new MockPayments();
        const mockPaymentsLayer = mockPayments.build();

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
            ownerAccountType: "user" as const,
            ownerDeletedAt: null,
            organizationId: project.organizationId,
            projectId: project.id,
            environmentId: environment.id,
            clawId: null,
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
            clawId: null,
          },
          modelPricing: mockPricing,
        };

        // Mock queue service
        const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const response = yield* handleNonStreamingResponse(
          proxyResult,
          context,
          validated,
        ).pipe(Effect.provide(mockQueueLayer));

        expect(response).toBeDefined();
        // Note: Metering now happens asynchronously via queue
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
            clawId: null,
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
            clawId: null,
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

  describe("enqueueRouterMetering", () => {
    it("successfully enqueues metering message", async () => {
      const sendMock = vi.fn().mockReturnValue(Effect.succeed(undefined));

      const usage = {
        inputTokens: 100,
        outputTokens: 50,
      };

      const request: RouterRequestIdentifiers = {
        userId: "user_123",
        organizationId: "org_123",
        projectId: "proj_123",
        environmentId: "env_123",
        apiKeyId: "key_123",
        routerRequestId: "req_123",
        clawId: null,
      };

      const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
        send: sendMock,
      });

      await Effect.runPromise(
        enqueueRouterMetering("req_123", "res_123", request, usage, 150).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      expect(sendMock).toHaveBeenCalledWith(
        expect.objectContaining({
          routerRequestId: "req_123",
          reservationId: "res_123",
          request,
          usage,
          costCenticents: 150,
          timestamp: expect.any(Number) as number,
        }),
      );
    });

    it("fails when queue send fails", async () => {
      const sendMock = vi
        .fn()
        .mockReturnValue(Effect.fail(new Error("Send failed")));

      const usage = {
        inputTokens: 100,
        outputTokens: 50,
      };

      const request: RouterRequestIdentifiers = {
        userId: "user_123",
        organizationId: "org_123",
        projectId: "proj_123",
        environmentId: "env_123",
        apiKeyId: "key_123",
        routerRequestId: "req_123",
        clawId: null,
      };

      const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
        send: sendMock,
      });

      await expect(
        Effect.runPromise(
          enqueueRouterMetering("req_123", "res_123", request, usage, 150).pipe(
            Effect.provide(mockQueueLayer),
          ),
        ),
      ).rejects.toThrow("Send failed");
    });

    it("handles non-Error object thrown by queue send", async () => {
      const sendMock = vi
        .fn()
        .mockReturnValue(Effect.fail(new Error("string error")));

      const usage = {
        inputTokens: 100,
        outputTokens: 50,
      };

      const request: RouterRequestIdentifiers = {
        userId: "user_123",
        organizationId: "org_123",
        projectId: "proj_123",
        environmentId: "env_123",
        apiKeyId: "key_123",
        routerRequestId: "req_123",
        clawId: null,
      };

      const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
        send: sendMock,
      });

      await expect(
        Effect.runPromise(
          enqueueRouterMetering("req_123", "res_123", request, usage, 150).pipe(
            Effect.provide(mockQueueLayer),
          ),
        ),
      ).rejects.toThrow("string error");
    });
  });
});
