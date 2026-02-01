/**
 * Unit tests for OpenAI provider router.
 *
 * Tests API mode routing and error handling.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

import type { Message } from "@/llm/messages";

import { user } from "@/llm/messages";

import { OpenAIProvider, chooseApiMode } from "./provider";

// Mock the OpenAI SDK
vi.mock("openai", async (importOriginal) => {
  const actual = await importOriginal<typeof import("openai")>();
  const mockCompletionsCreate = vi.fn();
  const mockResponsesCreate = vi.fn();

  // Create a mock class that mimics OpenAI client
  const MockOpenAI = vi.fn().mockImplementation(() => ({
    chat: {
      completions: {
        create: mockCompletionsCreate,
      },
    },
    responses: {
      create: mockResponsesCreate,
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

describe("OpenAIProvider", () => {
  let provider: OpenAIProvider;
  let mockCompletionsCreate: ReturnType<typeof vi.fn>;
  let mockResponsesCreate: ReturnType<typeof vi.fn>;

  const mockCompletionsResponse = {
    id: "chatcmpl-123",
    object: "chat.completion",
    created: 1677652288,
    model: "gpt-4o",
    choices: [
      {
        index: 0,
        message: {
          role: "assistant",
          content: "Hello!",
        },
        finish_reason: "stop",
      },
    ],
    usage: {
      prompt_tokens: 5,
      completion_tokens: 2,
      total_tokens: 7,
    },
  };

  const mockResponsesResponse = {
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
        content: [
          {
            type: "output_text",
            text: "Hello from Responses!",
            annotations: [],
          },
        ],
      },
    ],
    status: "completed",
    usage: {
      input_tokens: 5,
      output_tokens: 2,
      total_tokens: 7,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new OpenAIProvider({ apiKey: "test-key" });
    // Get the mock functions from the provider's sub-providers
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockCompletionsCreate = (provider as any).completionsProvider.client.chat
      .completions.create;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockResponsesCreate = (provider as any).responsesProvider.client.responses
      .create;
  });

  describe("constructor", () => {
    it("accepts custom baseURL", () => {
      const customProvider = new OpenAIProvider({
        apiKey: "test-key",
        baseURL: "https://custom.api.example.com",
      });
      expect(customProvider.id).toBe("openai");
    });
  });

  describe("API mode routing", () => {
    it("smart routes known models to responses API", async () => {
      mockResponsesCreate.mockResolvedValueOnce(mockResponsesResponse);

      const response = await provider.call({
        modelId: "openai/gpt-4o",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello from Responses!");
      expect(mockResponsesCreate).toHaveBeenCalled();
      expect(mockCompletionsCreate).not.toHaveBeenCalled();
    });

    it("routes to completions API with :completions suffix", async () => {
      mockCompletionsCreate.mockResolvedValueOnce(mockCompletionsResponse);

      const response = await provider.call({
        modelId: "openai/gpt-4o:completions",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello!");
      expect(mockCompletionsCreate).toHaveBeenCalled();
      expect(mockResponsesCreate).not.toHaveBeenCalled();
    });

    it("routes to responses API with :responses suffix", async () => {
      mockResponsesCreate.mockResolvedValueOnce(mockResponsesResponse);

      const response = await provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hi")],
      });

      expect(response.text()).toBe("Hello from Responses!");
      expect(mockResponsesCreate).toHaveBeenCalled();
      expect(mockCompletionsCreate).not.toHaveBeenCalled();
    });

    // Note: Audio routing integration test not included because audio encoding
    // is not yet implemented. The chooseApiMode unit tests verify the routing logic.
    // TODO: add this test when we introduce audio input support.
  });

  describe("call", () => {
    it("passes params to completions provider", async () => {
      mockCompletionsCreate.mockResolvedValueOnce(mockCompletionsResponse);

      await provider.call({
        modelId: "openai/gpt-4o:completions",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(mockCompletionsCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.5,
        }),
      );
    });

    it("passes params to responses provider", async () => {
      mockResponsesCreate.mockResolvedValueOnce(mockResponsesResponse);

      await provider.call({
        modelId: "openai/gpt-4o:responses",
        messages: [user("Hi")],
        params: { temperature: 0.5 },
      });

      expect(mockResponsesCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.5,
        }),
      );
    });
  });
});

describe("chooseApiMode", () => {
  const simpleMessages: Message[] = [user("Hello")];

  it("returns completions for :completions suffix", () => {
    expect(chooseApiMode("openai/gpt-4o:completions", simpleMessages)).toBe(
      "completions",
    );
  });

  it("returns responses for :responses suffix", () => {
    expect(chooseApiMode("openai/gpt-4o:responses", simpleMessages)).toBe(
      "responses",
    );
  });

  it("returns completions for audio content", () => {
    const messagesWithAudio: Message[] = [
      user([
        { type: "text", text: "Transcribe this" },
        {
          type: "audio",
          source: {
            type: "base64_audio_source",
            data: "audio-data",
            mimeType: "audio/wav",
          },
        },
      ]),
    ];
    expect(chooseApiMode("openai/gpt-4o", messagesWithAudio)).toBe(
      "completions",
    );
  });

  it("returns responses for known models with responses support", () => {
    expect(chooseApiMode("openai/gpt-4o", simpleMessages)).toBe("responses");
    expect(chooseApiMode("openai/gpt-4o-mini", simpleMessages)).toBe(
      "responses",
    );
  });

  it("returns completions for known models without responses support", () => {
    // gpt-3.5-turbo-16k only has :completions variant in KNOWN_MODELS
    expect(chooseApiMode("openai/gpt-3.5-turbo-16k", simpleMessages)).toBe(
      "completions",
    );
  });

  it("returns responses for unknown openai/ models", () => {
    expect(chooseApiMode("openai/gpt-99-future", simpleMessages)).toBe(
      "responses",
    );
  });

  it("returns completions for non-openai unknown models", () => {
    // Non-openai models (e.g., via OpenAI-compatible providers) default to completions
    expect(chooseApiMode("custom/some-model", simpleMessages)).toBe(
      "completions",
    );
  });

  it("ignores audio in system messages", () => {
    // System messages don't have audio content type, but this tests the skip logic
    const messagesWithSystem: Message[] = [
      {
        role: "system",
        content: { type: "text", text: "You are helpful" },
      },
      user("Hello"),
    ];
    expect(chooseApiMode("openai/gpt-4o", messagesWithSystem)).toBe(
      "responses",
    );
  });
});
