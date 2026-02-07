/**
 * E2E tests for document content in messages.
 *
 * Tests verify that documents are correctly encoded and sent to providers.
 */

import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { Document } from "@/llm/content";
import { user } from "@/llm/messages";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "document");

// Path to test PDF
const TEST_PDF_PATH = resolve(__dirname, "../assets/documents/test.pdf");

// URL to a publicly accessible PDF
const TEST_PDF_URL =
  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf";

/**
 * Providers for document tests. Uses non-reasoning models to avoid consuming
 * all tokens in reasoning before generating output.
 */
const DOCUMENT_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-haiku-4-5" },
  { providerId: "google", model: "google/gemini-2.5-flash" },
  { providerId: "openai:completions", model: "openai/gpt-4o-mini:completions" },
  { providerId: "openai:responses", model: "openai/gpt-4o-mini:responses" },
];

describe("document content", () => {
  // Test with base64-encoded document from file
  it.record.each(DOCUMENT_PROVIDERS)(
    "encodes base64 document",
    async ({ model }) => {
      const doc = Document.fromFile(TEST_PDF_PATH);
      const call = defineCall({
        model,
        maxTokens: 150,
        template: () => [
          user([
            "What text is in this PDF document? Reply in one short sentence.",
            doc,
          ]),
        ],
      });

      const snap = await snapshotTest(async (s) => {
        const response = await call();
        s.setResponse(response);

        // Response should describe the document content
        expect(response.text().length).toBeGreaterThan(0);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );

  // Test with URL-referenced document
  // Google doesn't support URL references, OpenAI Completions doesn't support URL file references
  it.record.each(
    DOCUMENT_PROVIDERS.filter(
      (p) => p.providerId !== "google" && p.providerId !== "openai:completions",
    ),
  )("encodes URL document", async ({ model }) => {
    const doc = Document.fromUrl(TEST_PDF_URL);
    const call = defineCall({
      model,
      maxTokens: 150,
      template: () => [
        user(["What is this PDF about? Reply in one short sentence.", doc]),
      ],
    });

    const snap = await snapshotTest(async (s) => {
      const response = await call();
      s.setResponse(response);

      expect(response.text().length).toBeGreaterThan(0);
    });

    expect(snap.toObject()).toMatchSnapshot();
  });
});
