/**
 * E2E tests for structured output formatting.
 *
 * These tests verify we correctly parse structured responses from LLMs.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";
import { z } from "zod";

import { defineCall } from "@/llm/calls";
import { defineFormat } from "@/llm/formatting";
import { PROVIDERS, type ProviderConfig } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

// Only Anthropic supports format/structured output currently
const FORMAT_PROVIDERS: ProviderConfig[] = PROVIDERS.filter(
  (p) => p.providerId === "anthropic",
);

const it = createIt(resolve(__dirname, "cassettes"), "format");

// Schema for structured output tests
const BookSchema = z.object({
  title: z.string().describe("The title of the book"),
  author: z.string().describe("The author of the book"),
  year: z.number().describe("The year published"),
});

type Book = z.infer<typeof BookSchema>;

describe("format output", () => {
  it.record.each(FORMAT_PROVIDERS)(
    "parses structured output with Zod schema",
    async ({ model }) => {
      const recommendBook = defineCall<{ genre: string }>()({
        model,
        maxTokens: 200,
        format: BookSchema,
        template: ({ genre }) =>
          `Recommend one famous ${genre} book. Return exactly one book.`,
      });

      const response = await recommendBook({ genre: "science fiction" });
      const book = response.parse();

      expect(book).toBeDefined();
      expect(typeof book.title).toBe("string");
      expect(typeof book.author).toBe("string");
      expect(typeof book.year).toBe("number");
      expect(book.title.length).toBeGreaterThan(0);
      expect(book.author.length).toBeGreaterThan(0);
      expect(book.year).toBeGreaterThan(1800);
    },
  );

  it.record.each(FORMAT_PROVIDERS)(
    "parses structured output with defineFormat",
    async ({ model }) => {
      const bookFormat = defineFormat<Book>({
        mode: "tool",
        validator: BookSchema,
      });

      const recommendBook = defineCall<{ genre: string }>()({
        model,
        maxTokens: 200,
        format: bookFormat,
        template: ({ genre }) =>
          `Recommend one famous ${genre} book. Return exactly one book.`,
      });

      const response = await recommendBook({ genre: "mystery" });
      const book = response.parse();

      expect(book).toBeDefined();
      expect(typeof book.title).toBe("string");
      expect(typeof book.author).toBe("string");
      expect(typeof book.year).toBe("number");
    },
  );
});
