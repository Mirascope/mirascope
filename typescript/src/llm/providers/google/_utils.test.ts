/**
 * Unit tests for Google provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping and thinking config encoding.
 */

import type { GenerateContentResponse } from "@google/genai";

import { describe, it, expect } from "vitest";

import type { AssistantMessage } from "@/llm/messages";

import { Document, Image } from "@/llm/content";
import {
  AuthenticationError,
  PermissionError,
  NotFoundError,
  RateLimitError,
  BadRequestError,
  ServerError,
  APIError,
  FeatureNotSupportedError,
} from "@/llm/exceptions";
import { user } from "@/llm/messages";

import {
  mapGoogleErrorByStatus,
  computeGoogleThinkingConfig,
  buildRequestParams,
  decodeResponse,
  encodeMessages,
} from "./_utils";

describe("mapGoogleErrorByStatus", () => {
  it("maps 401 to AuthenticationError", () => {
    expect(mapGoogleErrorByStatus(401)).toBe(AuthenticationError);
  });

  it("maps 403 to PermissionError", () => {
    expect(mapGoogleErrorByStatus(403)).toBe(PermissionError);
  });

  it("maps 404 to NotFoundError", () => {
    expect(mapGoogleErrorByStatus(404)).toBe(NotFoundError);
  });

  it("maps 429 to RateLimitError", () => {
    expect(mapGoogleErrorByStatus(429)).toBe(RateLimitError);
  });

  it("maps 400 to BadRequestError", () => {
    expect(mapGoogleErrorByStatus(400)).toBe(BadRequestError);
  });

  it("maps 422 to BadRequestError", () => {
    expect(mapGoogleErrorByStatus(422)).toBe(BadRequestError);
  });

  it("maps 5xx to ServerError", () => {
    expect(mapGoogleErrorByStatus(500)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(502)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(503)).toBe(ServerError);
  });

  it("maps unknown status codes to APIError", () => {
    expect(mapGoogleErrorByStatus(418)).toBe(APIError);
    expect(mapGoogleErrorByStatus(499)).toBe(APIError);
  });
});

describe("computeGoogleThinkingConfig", () => {
  describe("Gemini 2.5 models (budget-based)", () => {
    const modelId = "google/gemini-2.5-flash";

    it("returns dynamic budget (-1) for default level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "default" },
        8192,
        modelId,
      );
      expect(config.thinkingBudget).toBe(-1);
    });

    it("returns 0 budget for none level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "none" },
        8192,
        modelId,
      );
      expect(config.thinkingBudget).toBe(0);
    });

    it("computes budget based on multiplier for medium level", () => {
      // medium has multiplier 0.4
      const config = computeGoogleThinkingConfig(
        { level: "medium" },
        10000,
        modelId,
      );
      expect(config.thinkingBudget).toBe(4000);
    });

    it("sets includeThoughts when specified", () => {
      const config = computeGoogleThinkingConfig(
        { level: "medium", includeThoughts: true },
        8192,
        modelId,
      );
      expect(config.includeThoughts).toBe(true);
    });
  });

  describe("Gemini 3 Flash models (level-based)", () => {
    const modelId = "google/gemini-3-flash";

    it("returns MINIMAL for minimal level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "minimal" },
        8192,
        modelId,
      );
      expect(config.thinkingLevel).toBe("MINIMAL");
    });

    it("returns MEDIUM for medium level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "medium" },
        8192,
        modelId,
      );
      expect(config.thinkingLevel).toBe("MEDIUM");
    });
  });

  describe("Gemini 3 Pro models (level-based, LOW/HIGH only)", () => {
    const modelId = "google/gemini-3-pro";

    it("returns LOW for low level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "low" },
        8192,
        modelId,
      );
      expect(config.thinkingLevel).toBe("LOW");
    });

    it("returns HIGH for high level", () => {
      const config = computeGoogleThinkingConfig(
        { level: "high" },
        8192,
        modelId,
      );
      expect(config.thinkingLevel).toBe("HIGH");
    });
  });
});

describe("buildRequestParams thinking config", () => {
  it("sets thinkingConfig when thinking is specified", () => {
    const messages = [user("Hello")];

    const params = buildRequestParams(
      "google/gemini-2.5-flash",
      messages,
      undefined,
      {
        thinking: { level: "medium" },
        maxTokens: 10000,
      },
    );

    expect(params.config?.thinkingConfig).toEqual({
      thinkingBudget: 4000, // medium = 0.4 multiplier
    });
  });
});

describe("image encoding", () => {
  it("throws FeatureNotSupportedError for URL image source", () => {
    const urlImage = Image.fromUrl("https://example.com/image.png");
    const messages = [user(["Check this image", urlImage])];

    expect(() =>
      buildRequestParams("google/gemini-2.5-flash", messages, undefined, {}),
    ).toThrow(FeatureNotSupportedError);
  });
});

describe("document encoding", () => {
  it("encodes base64 document source as inlineData", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "base64_document_source",
        data: "JVBERi0xLjQ=",
        mediaType: "application/pdf",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams(
      "google/gemini-2.5-flash",
      messages,
      undefined,
      {},
    );

    const contents = params.contents as Array<{ parts?: unknown[] }>;
    const parts = contents[0]?.parts;
    expect(parts).toHaveLength(2);
    expect(parts?.[1]).toEqual({
      inlineData: {
        data: "JVBERi0xLjQ=",
        mimeType: "application/pdf",
      },
    });
  });

  it("encodes text document source as base64 inlineData", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "text_document_source",
        data: "Hello, world!",
        mediaType: "text/plain",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams(
      "google/gemini-2.5-flash",
      messages,
      undefined,
      {},
    );

    const contents = params.contents as Array<{ parts?: unknown[] }>;
    const parts = contents[0]?.parts;
    expect(parts).toHaveLength(2);
    expect(parts?.[1]).toEqual({
      inlineData: {
        data: btoa("Hello, world!"),
        mimeType: "text/plain",
      },
    });
  });

  it("throws FeatureNotSupportedError for URL document source", () => {
    const doc = Document.fromUrl("https://example.com/doc.pdf");
    const messages = [user(["Read this", doc])];

    expect(() =>
      buildRequestParams("google/gemini-2.5-flash", messages, undefined, {}),
    ).toThrow(FeatureNotSupportedError);
  });
});

describe("raw message round-tripping", () => {
  // Mock response for testing
  const mockGoogleResponse = {
    candidates: [
      {
        content: {
          role: "model",
          parts: [{ text: "Hello!" }],
        },
        finishReason: "STOP",
      },
    ],
    usageMetadata: {
      promptTokenCount: 10,
      candidatesTokenCount: 5,
      totalTokenCount: 15,
    },
    modelVersion: "gemini-2.5-flash",
  } as unknown as GenerateContentResponse;

  it("decodeResponse stores serialized content in rawMessage", () => {
    const { assistantMessage } = decodeResponse(
      mockGoogleResponse,
      "google/gemini-2.5-flash",
    );

    // rawMessage should be an object with role and parts
    expect(typeof assistantMessage.rawMessage).toBe("object");

    const rawMessage = assistantMessage.rawMessage as unknown as {
      role: string;
      parts: Array<Record<string, unknown>>;
    };
    expect(rawMessage.role).toBe("model");
    expect(Array.isArray(rawMessage.parts)).toBe(true);
    expect(rawMessage.parts[0]).toHaveProperty("text", "Hello!");
  });

  it("decodeResponse sets providerModelName from modelName", () => {
    const { assistantMessage } = decodeResponse(
      mockGoogleResponse,
      "google/gemini-2.5-flash",
    );

    // Should be the base model name (without provider prefix)
    expect(assistantMessage.providerModelName).toBe("gemini-2.5-flash");
  });

  it("encodeMessages reuses rawMessage for matching assistant messages", () => {
    // Create an assistant message that would have come from decodeResponse
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "google",
      modelId: "google/gemini-2.5-flash",
      providerModelName: "gemini-2.5-flash",
      rawMessage: {
        role: "model",
        parts: [{ text: "Hello!" }],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg, user("How are you?")];
    const { contents } = encodeMessages(messages, "google/gemini-2.5-flash");

    // Should have: user message, raw assistant message, user message
    expect(contents).toHaveLength(3);

    // First is user message
    expect(contents[0]).toEqual({
      role: "user",
      parts: [{ text: "Hi" }],
    });

    // Second should be the raw message reused directly
    expect(contents[1]).toHaveProperty("role", "model");
    expect(contents[1]).toHaveProperty("parts");
    expect((contents[1] as { parts: unknown[] }).parts[0]).toHaveProperty(
      "text",
      "Hello!",
    );

    // Third is user message
    expect(contents[2]).toEqual({
      role: "user",
      parts: [{ text: "How are you?" }],
    });
  });

  it("encodeMessages does NOT reuse rawMessage for different provider", () => {
    // Create an assistant message from a different provider
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "anthropic", // Different provider
      modelId: "anthropic/claude-haiku-4-5",
      providerModelName: "claude-haiku-4-5",
      rawMessage: {
        role: "assistant",
        content: [{ type: "text", text: "Hello!" }],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const { contents } = encodeMessages(messages, "google/gemini-2.5-flash");

    // Should encode from content, not raw message
    expect(contents).toHaveLength(2);
    expect(contents[1]).toEqual({
      role: "model",
      parts: [{ text: "Hello!" }],
    });
  });

  it("encodeMessages does NOT reuse rawMessage for different model", () => {
    // Create an assistant message from a different model
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "google",
      modelId: "google/gemini-2.5-pro", // Different model
      providerModelName: "gemini-2.5-pro",
      rawMessage: {
        role: "model",
        parts: [{ text: "Hello!" }],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    // Request is for flash, but message is from pro
    const { contents } = encodeMessages(messages, "google/gemini-2.5-flash");

    // Should encode from content, not raw message
    expect(contents).toHaveLength(2);
    expect(contents[1]).toEqual({
      role: "model",
      parts: [{ text: "Hello!" }],
    });
  });

  it("encodeMessages reuses rawMessage without structure validation", () => {
    // Create an assistant message with non-standard rawMessage
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "google",
      modelId: "google/gemini-2.5-flash",
      providerModelName: "gemini-2.5-flash",
      rawMessage: {
        // Even without proper 'role' and 'parts' structure
        text: "Hello!",
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const { contents } = encodeMessages(messages, "google/gemini-2.5-flash");

    // rawMessage IS reused
    expect(contents).toHaveLength(2);
    expect(contents[1]).toEqual({ text: "Hello!" });
  });
});
