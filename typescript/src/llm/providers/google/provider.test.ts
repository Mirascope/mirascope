/**
 * Unit tests for Google provider.
 *
 * Tests error handling by mocking the SDK client to throw errors.
 */

import { ApiError } from "@google/genai";
import { describe, it, expect, vi, beforeEach } from "vitest";

import {
  AuthenticationError,
  BadRequestError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
  APIError,
} from "@/llm/exceptions";
import { user } from "@/llm/messages";

import { GoogleProvider } from "./provider";

// Mock the Google SDK
vi.mock("@google/genai", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@google/genai")>();
  return {
    ...actual,
    GoogleGenAI: vi.fn().mockImplementation(() => ({
      models: {
        generateContent: vi.fn(),
      },
    })),
  };
});

/**
 * Create an ApiError with the given status code.
 * The SDK's ApiError requires setting status after construction.
 */
function createApiError(message: string, status: number): ApiError {
  const error = new ApiError({ status: 418, message });
  error.status = status;
  // Also set the message since the constructor doesn't accept it
  Object.defineProperty(error, "message", { value: message });
  return error;
}

describe("GoogleProvider", () => {
  let provider: GoogleProvider;
  let mockGenerateContent: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new GoogleProvider({ apiKey: "test-key" });
    // Get the mock function from the provider's client
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockGenerateContent = (provider as any).client.models.generateContent;
  });

  describe("constructor", () => {
    it("accepts custom baseURL", () => {
      const customProvider = new GoogleProvider({
        apiKey: "test-key",
        baseURL: "https://custom.api.example.com",
      });
      expect(customProvider.id).toBe("google");
    });
  });

  describe("call", () => {
    const mockResponse = {
      candidates: [
        {
          content: { parts: [{ text: "Hello!" }], role: "model" },
          finishReason: "STOP",
        },
      ],
      usageMetadata: { promptTokenCount: 5, candidatesTokenCount: 2 },
      modelVersion: "gemini-2.0-flash",
    };

    it("returns response with params when provided", async () => {
      mockGenerateContent.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "google/gemini-2.0-flash",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(response.text()).toBe("Hello!");
    });

    it("returns response without params", async () => {
      mockGenerateContent.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: "google/gemini-2.0-flash",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello!");
    });
  });

  describe("error handling", () => {
    const testCases = [
      {
        status: 401,
        ErrorClass: AuthenticationError,
        name: "AuthenticationError",
      },
      { status: 403, ErrorClass: PermissionError, name: "PermissionError" },
      { status: 404, ErrorClass: NotFoundError, name: "NotFoundError" },
      { status: 429, ErrorClass: RateLimitError, name: "RateLimitError" },
      { status: 400, ErrorClass: BadRequestError, name: "BadRequestError" },
      { status: 422, ErrorClass: BadRequestError, name: "BadRequestError" },
      { status: 500, ErrorClass: ServerError, name: "ServerError" },
      { status: 502, ErrorClass: ServerError, name: "ServerError" },
      { status: 503, ErrorClass: ServerError, name: "ServerError" },
      { status: 418, ErrorClass: APIError, name: "APIError" },
    ];

    for (const { status, ErrorClass, name } of testCases) {
      it(`wraps ${status} ApiError as ${name}`, async () => {
        const apiError = createApiError(`Error with status ${status}`, status);
        mockGenerateContent.mockRejectedValueOnce(apiError);

        const callPromise = provider.call({
          modelId: "google/gemini-2.0-flash",
          messages: [user("Hello")],
        });

        await expect(callPromise).rejects.toBeInstanceOf(ErrorClass);
        await expect(callPromise).rejects.toMatchObject({
          message: `Error with status ${status}`,
          provider: "google",
          statusCode: status,
        });
      });
    }

    it("preserves original ApiError as originalException", async () => {
      const apiError = createApiError("Original error", 401);
      mockGenerateContent.mockRejectedValueOnce(apiError);

      try {
        await provider.call({
          modelId: "google/gemini-2.0-flash",
          messages: [user("Hello")],
        });
        expect.fail("Expected error to be thrown");
      } catch (e) {
        expect(e).toBeInstanceOf(AuthenticationError);
        expect((e as AuthenticationError).originalException).toBe(apiError);
      }
    });

    it("re-throws non-ApiError errors as-is", async () => {
      const genericError = new Error("Network failure");
      mockGenerateContent.mockRejectedValueOnce(genericError);

      const callPromise = provider.call({
        modelId: "google/gemini-2.0-flash",
        messages: [user("Hello")],
      });

      // Base class returns non-mapped errors unchanged
      await expect(callPromise).rejects.toBe(genericError);
    });
  });
});
