/**
 * Unit tests for OpenAI Responses provider.
 *
 * Tests error handling by mocking the SDK client to throw errors.
 */

import OpenAI from "openai";
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
  TimeoutError,
} from "@/llm/exceptions";
import { user } from "@/llm/messages";

import { OpenAIResponsesProvider } from "./provider";

// Mock the OpenAI SDK
vi.mock("openai", async (importOriginal) => {
  const actual = await importOriginal<typeof import("openai")>();
  const mockCreate = vi.fn();

  // Create a mock class that mimics OpenAI client
  const MockOpenAI = vi.fn().mockImplementation(() => ({
    responses: {
      create: mockCreate,
    },
  }));

  // Attach the error classes to the mock
  Object.assign(MockOpenAI, {
    AuthenticationError: actual.default.AuthenticationError,
    PermissionDeniedError: actual.default.PermissionDeniedError,
    BadRequestError: actual.default.BadRequestError,
    NotFoundError: actual.default.NotFoundError,
    RateLimitError: actual.default.RateLimitError,
    InternalServerError: actual.default.InternalServerError,
    APIError: actual.default.APIError,
    APIConnectionError: actual.default.APIConnectionError,
    APIConnectionTimeoutError: actual.default.APIConnectionTimeoutError,
    UnprocessableEntityError: actual.default.UnprocessableEntityError,
    ConflictError: actual.default.ConflictError,
  });

  return {
    ...actual,
    default: MockOpenAI,
  };
});

/**
 * Create an OpenAI SDK error with the correct constructor signature.
 */
function createSdkError(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ErrorClass: new (...args: any[]) => InstanceType<typeof OpenAI.APIError>,
  message: string,
  status: number,
): InstanceType<typeof OpenAI.APIError> {
  return new ErrorClass(status, { message }, message, new Headers());
}

describe("OpenAIResponsesProvider", () => {
  let provider: OpenAIResponsesProvider;
  let mockCreate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new OpenAIResponsesProvider({ apiKey: "test-key" });
    // Get the mock function from the provider's client
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockCreate = (provider as any).client.responses.create;
  });

  describe("constructor", () => {
    it("accepts custom baseURL", () => {
      const customProvider = new OpenAIResponsesProvider({
        apiKey: "test-key",
        baseURL: "https://custom.api.example.com",
      });
      expect(customProvider.id).toBe("openai");
    });
  });

  describe("call", () => {
    const mockResponse = {
      id: "resp_123",
      object: "response",
      created_at: 1677652288,
      model: "gpt-4o",
      output: [
        {
          type: "message",
          id: "msg_123",
          status: "completed",
          role: "assistant",
          content: [{ type: "output_text", text: "Hello!", annotations: [] }],
        },
      ],
      status: "completed",
      usage: {
        input_tokens: 5,
        output_tokens: 2,
        total_tokens: 7,
      },
    };

    it("returns response with params when provided", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(response.text()).toBe("Hello!");
    });

    it("returns response without params", async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello!");
    });
  });

  describe("error handling", () => {
    const testCases = [
      {
        ErrorClass: OpenAI.AuthenticationError,
        MirascopeError: AuthenticationError,
        name: "AuthenticationError",
        status: 401,
      },
      {
        ErrorClass: OpenAI.PermissionDeniedError,
        MirascopeError: PermissionError,
        name: "PermissionError",
        status: 403,
      },
      {
        ErrorClass: OpenAI.BadRequestError,
        MirascopeError: BadRequestError,
        name: "BadRequestError",
        status: 400,
      },
      {
        ErrorClass: OpenAI.NotFoundError,
        MirascopeError: NotFoundError,
        name: "NotFoundError",
        status: 404,
      },
      {
        ErrorClass: OpenAI.RateLimitError,
        MirascopeError: RateLimitError,
        name: "RateLimitError",
        status: 429,
      },
      {
        ErrorClass: OpenAI.InternalServerError,
        MirascopeError: ServerError,
        name: "ServerError",
        status: 500,
      },
      {
        ErrorClass: OpenAI.UnprocessableEntityError,
        MirascopeError: BadRequestError,
        name: "BadRequestError (from UnprocessableEntityError)",
        status: 422,
      },
      {
        ErrorClass: OpenAI.ConflictError,
        MirascopeError: BadRequestError,
        name: "BadRequestError (from ConflictError)",
        status: 409,
      },
      {
        ErrorClass: OpenAI.APIError,
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
          modelId: "openai/gpt-4o:responses",
          messages: [user("Hello")],
        });

        await expect(callPromise).rejects.toBeInstanceOf(MirascopeError);
        await expect(callPromise).rejects.toMatchObject({
          provider: "openai",
        });
      });
    }

    it("wraps APIConnectionError as ConnectionError", async () => {
      // APIConnectionError has a different constructor signature
      const sdkError = new OpenAI.APIConnectionError({
        cause: new Error("Connection failed"),
      });
      mockCreate.mockRejectedValueOnce(sdkError);

      const callPromise = provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hello")],
      });

      await expect(callPromise).rejects.toBeInstanceOf(ConnectionError);
      await expect(callPromise).rejects.toMatchObject({
        provider: "openai",
      });
    });

    it("wraps APIConnectionTimeoutError as TimeoutError", async () => {
      const sdkError = new OpenAI.APIConnectionTimeoutError();
      mockCreate.mockRejectedValueOnce(sdkError);

      const callPromise = provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hello")],
      });

      await expect(callPromise).rejects.toBeInstanceOf(TimeoutError);
      await expect(callPromise).rejects.toMatchObject({
        provider: "openai",
      });
    });

    it("preserves original error as originalException", async () => {
      const sdkError = createSdkError(
        OpenAI.AuthenticationError,
        "Invalid API key",
        401,
      );
      mockCreate.mockRejectedValueOnce(sdkError);

      try {
        await provider.call({
          modelId: "openai/gpt-4o:responses",
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
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hello")],
      });

      // Base class returns non-mapped errors unchanged
      await expect(callPromise).rejects.toBe(genericError);
    });
  });
});
