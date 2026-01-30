import { describe, expect, it } from "vitest";

import type { Image } from "@/llm/content/image";
import type { Message } from "@/llm/messages/message";

import { isMessages, promoteToMessages } from "@/llm/messages/utils";

describe("isMessages", () => {
  it("returns true for an array of SystemMessages", () => {
    const messages: Message[] = [
      { role: "system", content: { type: "text", text: "System prompt" } },
    ];

    expect(isMessages(messages)).toBe(true);
  });

  it("returns true for an array of UserMessages", () => {
    const messages: Message[] = [
      {
        role: "user",
        content: [{ type: "text", text: "Hello" }],
        name: null,
      },
    ];

    expect(isMessages(messages)).toBe(true);
  });

  it("returns true for an array of AssistantMessages", () => {
    const messages: Message[] = [
      {
        role: "assistant",
        content: [{ type: "text", text: "Hi there!" }],
        name: null,
        providerId: null,
        modelId: null,
        providerModelName: null,
        rawMessage: null,
      },
    ];

    expect(isMessages(messages)).toBe(true);
  });

  it("returns true for mixed message types", () => {
    const messages: Message[] = [
      { role: "system", content: { type: "text", text: "System" } },
      {
        role: "user",
        content: [{ type: "text", text: "User" }],
        name: null,
      },
      {
        role: "assistant",
        content: [{ type: "text", text: "Assistant" }],
        name: null,
        providerId: null,
        modelId: null,
        providerModelName: null,
        rawMessage: null,
      },
    ];

    expect(isMessages(messages)).toBe(true);
  });

  it("returns false for a string", () => {
    expect(isMessages("Hello")).toBe(false);
  });

  it("returns false for a UserContentPart", () => {
    const textPart = { type: "text" as const, text: "Hello" };

    expect(isMessages(textPart)).toBe(false);
  });

  it("returns false for an array of strings", () => {
    expect(isMessages(["Hello", "World"])).toBe(false);
  });

  it("returns false for an array of UserContentParts", () => {
    const parts = [
      { type: "text" as const, text: "Hello" },
      { type: "text" as const, text: "World" },
    ];

    expect(isMessages(parts)).toBe(false);
  });

  it("returns false for an array with mixed content types", () => {
    const image: Image = {
      type: "image",
      source: { type: "url_image_source", url: "https://example.com/img.png" },
    };
    const parts = ["Hello", image];

    expect(isMessages(parts)).toBe(false);
  });

  it("throws an error for an empty array", () => {
    expect(() => isMessages([])).toThrow(
      "Empty array may not be used as message content",
    );
  });
});

describe("promoteToMessages", () => {
  it("returns messages as-is when given messages", () => {
    const messages: Message[] = [
      { role: "system", content: { type: "text", text: "System" } },
      {
        role: "user",
        content: [{ type: "text", text: "Hello" }],
        name: null,
      },
    ];

    expect(promoteToMessages(messages)).toBe(messages);
  });

  it("wraps a string in a user message", () => {
    const result = promoteToMessages("Hello");

    expect(result).toEqual([
      {
        role: "user",
        content: [{ type: "text", text: "Hello" }],
        name: null,
      },
    ]);
  });

  it("wraps a UserContentPart in a user message", () => {
    const textPart = { type: "text" as const, text: "Hello" };
    const result = promoteToMessages(textPart);

    expect(result).toEqual([
      {
        role: "user",
        content: [textPart],
        name: null,
      },
    ]);
  });

  it("wraps an array of strings in a user message", () => {
    const result = promoteToMessages(["Hello", "World"]);

    expect(result).toEqual([
      {
        role: "user",
        content: [
          { type: "text", text: "Hello" },
          { type: "text", text: "World" },
        ],
        name: null,
      },
    ]);
  });

  it("wraps an array of UserContentParts in a user message", () => {
    const image: Image = {
      type: "image",
      source: { type: "url_image_source", url: "https://example.com/img.png" },
    };
    const result = promoteToMessages(["Look at this:", image]);

    expect(result).toEqual([
      {
        role: "user",
        content: [{ type: "text", text: "Look at this:" }, image],
        name: null,
      },
    ]);
  });
});
