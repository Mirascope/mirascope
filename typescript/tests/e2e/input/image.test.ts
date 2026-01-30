/**
 * E2E tests for image content in messages.
 *
 * Tests verify that images are correctly encoded and sent to providers.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { Image } from "@/llm/content";
import { user } from "@/llm/messages";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "image");

// Path to test image
const WIKIPEDIA_ICON_PATH = resolve(
  __dirname,
  "../assets/images/wikipedia.png",
);

// URL to the same image online
const WIKIPEDIA_ICON_URL =
  "https://en.wikipedia.org/static/images/icons/wikipedia.png";

/**
 * Providers for image tests. Uses non-reasoning models to avoid consuming
 * all tokens in reasoning before generating output.
 */
const IMAGE_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-haiku-4-5" },
  { providerId: "google", model: "google/gemini-2.5-flash" },
  { providerId: "openai:completions", model: "openai/gpt-4o-mini:completions" },
  { providerId: "openai:responses", model: "openai/gpt-4o-mini:responses" },
];

/**
 * Load the test image as base64.
 */
function loadTestImage(): Image {
  const data = readFileSync(WIKIPEDIA_ICON_PATH);
  return Image.fromBytes(new Uint8Array(data));
}

describe("image content", () => {
  // Test with base64-encoded image from file
  it.record.each(IMAGE_PROVIDERS)("encodes base64 image", async ({ model }) => {
    const image = loadTestImage();
    const call = defineCall({
      model,
      maxTokens: 150,
      template: () => [
        user(["Describe this image in one short sentence.", image]),
      ],
    });

    const response = await call();

    // Response should describe something about the image (Wikipedia logo)
    expect(response.text().length).toBeGreaterThan(0);
  });

  // Test with URL-referenced image
  // Google requires downloading images first, so URL references are not supported
  // OpenAI Responses API sometimes fails to download URLs, so we test with Completions only
  it.record.each(
    IMAGE_PROVIDERS.filter(
      (p) => p.providerId !== "google" && p.providerId !== "openai:responses",
    ),
  )("encodes URL image", async ({ model }) => {
    const image = Image.fromUrl(WIKIPEDIA_ICON_URL);
    const call = defineCall({
      model,
      maxTokens: 150,
      template: () => [
        user(["Describe this image in one short sentence.", image]),
      ],
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });
});
