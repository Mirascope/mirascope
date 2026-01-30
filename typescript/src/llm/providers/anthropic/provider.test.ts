/**
 * Unit tests for Anthropic provider.
 *
 * Tests error handling by mocking the SDK client to throw errors.
 */

import Anthropic from "@anthropic-ai/sdk";
import { describe, it, expect, vi, beforeEach } from "vitest";

import {
  AuthenticationError,
  BadRequestError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
  APIError,
  ConnectionError,
} from "@/llm/exceptions";
import { user } from "@/llm/messages";

import { AnthropicProvider } from "./provider";

// Mock the Anthropic SDK
vi.mock("@anthropic-ai/sdk", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@anthropic-ai/sdk")>();
  const mockCreate = vi.fn();

  // Create a mock class that mimics Anthropic client
  const MockAnthropic = vi.fn().mockImplementation(() => ({
    messages: {
      create: mockCreate,
    },
  }));

  // Attach the error classes to the mock
  Object.assign(MockAnthropic, {
    AuthenticationError: actual.default.AuthenticationError,
    PermissionDeniedError: actual.default.PermissionDeniedError,
    BadRequestError: actual.default.BadRequestError,
    NotFoundError: actual.default.NotFoundError,
    RateLimitError: actual.default.RateLimitError,
    InternalServerError: actual.default.InternalServerError,
    APIError: actual.default.APIError,
    APIConnectionError: actual.default.APIConnectionError,
  });

  return {
    ...actual,
    default: MockAnthropic,
  };
});

/**
 * Create an Anthropic SDK error with the correct constructor signature.
 * Uses type assertion to work around the SDK's complex generic types.
 */
function createSdkError(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ErrorClass: new (...args: any[]) => InstanceType<typeof Anthropic.APIError>,
  message: string,
  status: number,
): InstanceType<typeof Anthropic.APIError> {
  return new ErrorClass(
    status,
    { type: "error", error: { type: "api_error", message } },
    message,
    new Headers(),
  );
}

describe("AnthropicProvider", () => {
  let provider: AnthropicProvider;
  let mockCreate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new AnthropicProvider({ apiKey: "test-key" });
    // Get the mock function from the provider's client
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockCreate = (provider as any).client.messages.create;
  });

  describe("constructor", () => {
    it("accepts custom baseURL", () => {
      const customProvider = new AnthropicProvider({
        apiKey: "test-key",
        baseURL: "https://custom.api.example.com",
      });
      expect(customProvider.id).toBe("anthropic");
    });
  });

  describe("call", () => {
    const mockResponse = {
      id: "msg_123",
      type: "message",
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      model: "claude-haiku-4-5",
      stop_reason: "end_turn",
      usage: { input_tokens: 5, output_tokens: 2 },
    };

    it("returns response with params when provided", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "anthropic/claude-haiku-4-5",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(response.text()).toBe("Hello!");
    });

    it("returns response without params", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "anthropic/claude-haiku-4-5",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello!");
    });
  });

  describe("error handling", () => {
    const testCases = [
      {
        ErrorClass: Anthropic.AuthenticationError,
        MirascopeError: AuthenticationError,
        name: "AuthenticationError",
        status: 401,
      },
      {
        ErrorClass: Anthropic.PermissionDeniedError,
        MirascopeError: PermissionError,
        name: "PermissionError",
        status: 403,
      },
      {
        ErrorClass: Anthropic.BadRequestError,
        MirascopeError: BadRequestError,
        name: "BadRequestError",
        status: 400,
      },
      {
        ErrorClass: Anthropic.NotFoundError,
        MirascopeError: NotFoundError,
        name: "NotFoundError",
        status: 404,
      },
      {
        ErrorClass: Anthropic.RateLimitError,
        MirascopeError: RateLimitError,
        name: "RateLimitError",
        status: 429,
      },
      {
        ErrorClass: Anthropic.InternalServerError,
        MirascopeError: ServerError,
        name: "ServerError",
        status: 500,
      },
      {
        ErrorClass: Anthropic.APIError,
        MirascopeError: APIError,
        name: "APIError",
        status: 418,
      },
    ];

    for (const { ErrorClass, MirascopeError, name, status } of testCases) {
      it(`wraps ${ErrorClass.name} as ${name}`, async () => {
        const sdkError = createSdkError(ErrorClass, `Test ${name}`, status);
        mockCreate.mockRejectedValueOnce(sdkError);

        const callPromise = provider.call({
          modelId: "anthropic/claude-haiku-4-5",
          messages: [user("Hello")],
        });

        await expect(callPromise).rejects.toBeInstanceOf(MirascopeError);
        await expect(callPromise).rejects.toMatchObject({
          provider: "anthropic",
        });
      });
    }

    it("wraps APIConnectionError as ConnectionError", async () => {
      // APIConnectionError has a different constructor signature
      const sdkError = new Anthropic.APIConnectionError({
        cause: new Error("Connection failed"),
      });
      mockCreate.mockRejectedValueOnce(sdkError);

      const callPromise = provider.call({
        modelId: "anthropic/claude-haiku-4-5",
        messages: [user("Hello")],
      });

      await expect(callPromise).rejects.toBeInstanceOf(ConnectionError);
      await expect(callPromise).rejects.toMatchObject({
        provider: "anthropic",
      });
    });

    it("preserves original error as originalException", async () => {
      const sdkError = createSdkError(
        Anthropic.AuthenticationError,
        "Invalid API key",
        401,
      );
      mockCreate.mockRejectedValueOnce(sdkError);

      try {
        await provider.call({
          modelId: "anthropic/claude-haiku-4-5",
          messages: [user("Hello")],
        });
        expect.fail("Expected error to be thrown");
      } catch (e) {
        expect(e).toBeInstanceOf(AuthenticationError);
        expect((e as AuthenticationError).originalException).toBe(sdkError);
      }
    });

    it("re-throws non-SDK errors as-is", async () => {
      const genericError = new Error("Network failure");
      mockCreate.mockRejectedValueOnce(genericError);

      const callPromise = provider.call({
        modelId: "anthropic/claude-haiku-4-5",
        messages: [user("Hello")],
      });

      // Base class returns non-mapped errors unchanged
      await expect(callPromise).rejects.toBe(genericError);
    });
  });
});
