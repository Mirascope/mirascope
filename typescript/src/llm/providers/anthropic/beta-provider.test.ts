/**
 * Unit tests for Anthropic Beta provider.
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

import { AnthropicBetaProvider } from "./beta-provider";

// Mock the Anthropic SDK
vi.mock("@anthropic-ai/sdk", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@anthropic-ai/sdk")>();
  const mockCreate = vi.fn();

  // Create a mock class that mimics Anthropic client with beta.messages
  const MockAnthropic = vi.fn().mockImplementation(() => ({
    messages: {
      create: vi.fn(),
    },
    beta: {
      messages: {
        create: mockCreate,
      },
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

describe("AnthropicBetaProvider", () => {
  let provider: AnthropicBetaProvider;
  let mockCreate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new AnthropicBetaProvider({ apiKey: "test-key" });
    // Get the mock function from the provider's beta.messages client
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockCreate = (provider as any).client.beta.messages.create;
  });

  describe("constructor", () => {
    it("has correct provider id", () => {
      expect(provider.id).toBe("anthropic-beta");
    });

    it("accepts custom baseURL", () => {
      const customProvider = new AnthropicBetaProvider({
        apiKey: "test-key",
        baseURL: "https://custom.api.example.com",
      });
      expect(customProvider.id).toBe("anthropic-beta");
    });
  });

  describe("call", () => {
    const mockResponse = {
      id: "msg_beta_123",
      type: "message",
      role: "assistant",
      content: [{ type: "text", text: "Hello from beta!", citations: null }],
      model: "claude-haiku-4-5",
      stop_reason: "end_turn",
      stop_sequence: null,
      usage: {
        input_tokens: 5,
        output_tokens: 3,
        cache_read_input_tokens: 0,
        cache_creation_input_tokens: 0,
        cache_creation: null,
        server_tool_use: null,
      },
      container: null,
    };

    it("returns response with params when provided", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "anthropic-beta/claude-haiku-4-5",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(response.text()).toBe("Hello from beta!");
    });

    it("returns response without params", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "anthropic-beta/claude-haiku-4-5",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello from beta!");
    });

    it("uses beta API endpoint", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      await provider.call({
        modelId: "anthropic-beta/claude-haiku-4-5",
        messages: [user("Hi")],
      });

      expect(mockCreate).toHaveBeenCalledTimes(1);
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
          modelId: "anthropic-beta/claude-haiku-4-5",
          messages: [user("Hello")],
        });

        await expect(callPromise).rejects.toBeInstanceOf(MirascopeError);
        await expect(callPromise).rejects.toMatchObject({
          provider: "anthropic-beta",
        });
      });
    }

    it("wraps APIConnectionError as ConnectionError", async () => {
      const sdkError = new Anthropic.APIConnectionError({
        cause: new Error("Connection failed"),
      });
      mockCreate.mockRejectedValueOnce(sdkError);

      const callPromise = provider.call({
        modelId: "anthropic-beta/claude-haiku-4-5",
        messages: [user("Hello")],
      });

      await expect(callPromise).rejects.toBeInstanceOf(ConnectionError);
      await expect(callPromise).rejects.toMatchObject({
        provider: "anthropic-beta",
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
          modelId: "anthropic-beta/claude-haiku-4-5",
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
        modelId: "anthropic-beta/claude-haiku-4-5",
        messages: [user("Hello")],
      });

      await expect(callPromise).rejects.toBe(genericError);
    });
  });
});
