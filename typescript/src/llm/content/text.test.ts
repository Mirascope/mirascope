import { describe, expect, it } from "vitest";

import type { Text } from "@/llm/content/text";

describe("Text", () => {
  it("has correct type discriminator", () => {
    const text: Text = { type: "text", text: "hello world" };
    expect(text.type).toBe("text");
  });

  it("stores text content", () => {
    const text: Text = { type: "text", text: "hello world" };
    expect(text.text).toBe("hello world");
  });

  it("supports empty text", () => {
    const text: Text = { type: "text", text: "" };
    expect(text.text).toBe("");
  });

  it("supports multiline text", () => {
    const text: Text = { type: "text", text: "line1\nline2\nline3" };
    expect(text.text).toBe("line1\nline2\nline3");
  });
});
