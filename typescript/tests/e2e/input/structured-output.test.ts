/**
 * E2E tests for structured output features.
 *
 * Tests verify structured output streaming, primitive types, and formatting instructions.
 */

import { resolve } from "node:path";
import { z } from "zod";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "structured-output");

/**
 * Book schema for structured output tests.
 */
const BookReviewSchema = z.object({
  title: z.string().describe("The title of the book"),
  author: z.string().describe("The author of the book"),
  themes: z.array(z.string()).describe("Main themes of the book"),
  rating: z.number().int().min(1).max(10).describe("Rating from 1 to 10"),
});

/**
 * Providers for structured output tests.
 * Testing on Anthropic since it has good structured output support.
 */
const STRUCTURED_OUTPUT_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-haiku-4-5" },
];

describe("structured output streaming", () => {
  it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
    "streams partial objects",
    async ({ model }) => {
      const recommendBook = defineCall({
        model,
        maxTokens: 300,
        format: BookReviewSchema,
        template: () =>
          "Please recommend a book and provide a detailed review!",
      });

      const snap = await snapshotTest(async (s) => {
        const stream = await recommendBook.stream();
        const partials: unknown[] = [];

        for await (const partial of stream.structuredStream()) {
          partials.push(partial);
        }

        s.setResponse(stream);
        s.set("nPartials", partials.length);

        // Verify we got multiple partial updates
        expect(partials.length).toBeGreaterThan(1);

        // Final result should be complete
        const finalResult = await stream.parse();
        expect(finalResult.title).toBeDefined();
        expect(finalResult.author).toBeDefined();
        expect(finalResult.rating).toBeDefined();
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );
});

// Note: Primitive type formats (z.array(), z.number()) are not yet supported.
// Structured output requires object schemas with z.object().

describe("structured output with formatting instructions", () => {
  it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
    "respects schema descriptions as formatting hints",
    async ({ model }) => {
      // Create a schema with explicit formatting hints in descriptions
      const BookWithHintsSchema = z.object({
        title: z.string().describe("The title of the book (use all caps)"),
        author: z.string().describe("The author of the book"),
        rating: z.number().int().describe("Rating should always be 7"),
      });

      const recommendBook = defineCall<{ bookName: string }>()({
        model,
        maxTokens: 200,
        format: BookWithHintsSchema,
        template: ({ bookName }) =>
          `Recommend "${bookName}" by Patrick Rothfuss. Follow the field descriptions exactly.`,
      });

      const snap = await snapshotTest(async (s) => {
        const response = await recommendBook({
          bookName: "The Name of the Wind",
        });
        s.setResponse(response);

        const book = response.parse();
        s.set("parsedBook", book);

        // Verify the response has expected structure
        expect(book.author).toBeDefined();
        expect(book.title).toBeDefined();
        expect(typeof book.rating).toBe("number");
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );
});
