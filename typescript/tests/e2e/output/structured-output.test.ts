/**
 * E2E tests for structured output.
 *
 * Tests verify structured output parsing with nested schemas,
 * different formatting modes, and streaming.
 */

import { resolve } from "node:path";
import { z } from "zod";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { createContext, type Context } from "@/llm/context";
import { defineFormat, type FormattingMode } from "@/llm/formatting";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "structured-output");

/**
 * Nested author schema.
 */
const AuthorSchema = z.object({
  firstName: z.string().describe("The author's first name"),
  lastName: z.string().describe("The author's last name"),
});

/**
 * Book schema with nested author and specific instructions in descriptions.
 */
const BookSchema = z.object({
  title: z.string().describe("The title of the book (should be in all caps)"),
  author: AuthorSchema.describe("The author of the book"),
  rating: z
    .number()
    .int()
    .describe("For testing purposes, the rating should be 7"),
});

type Book = z.infer<typeof BookSchema>;

/**
 * Providers that support structured output.
 */
const STRUCTURED_OUTPUT_PROVIDERS: ProviderConfig[] = PROVIDERS.filter(
  (p) => p.providerId === "anthropic",
);

/**
 * Helper to create format based on mode.
 */
function createFormat(mode: FormattingMode | null) {
  return mode !== null
    ? defineFormat<Book>({ mode, validator: BookSchema })
    : BookSchema;
}

/**
 * Tests for each formatting mode.
 */
const MODES: { mode: FormattingMode | null; label: string }[] = [
  { mode: "tool", label: "tool mode" },
  { mode: "json", label: "json mode" },
  { mode: null, label: "default mode" },
];

for (const { mode, label } of MODES) {
  const modeSlug = mode ?? "default";
  describe(`structured output (${label})`, () => {
    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `parses with nested schema (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const recommendBook = defineCall<{ author: string }>()({
          model,
          maxTokens: 300,
          format,
          template: ({ author }) =>
            `Please recommend the most popular book by ${author}`,
        });

        const snap = await snapshotTest(async (s) => {
          const response = await recommendBook({ author: "Patrick Rothfuss" });
          s.setResponse(response);

          const book = response.parse();
          s.set("parsedBook", book);

          expect(book.author.firstName).toBe("Patrick");
          expect(book.author.lastName).toBe("Rothfuss");
          expect(book.title).toBe("THE NAME OF THE WIND");
          expect(book.rating).toBe(7);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );

    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `parses with context (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const recommendBook = defineCall<{ ctx: Context<string> }>()({
          model,
          maxTokens: 300,
          format,
          template: ({ ctx }) =>
            `Please recommend the most popular book by ${ctx.deps}`,
        });

        const snap = await snapshotTest(async (s) => {
          const ctx = createContext<string>("Patrick Rothfuss");
          const response = await recommendBook(ctx);
          s.setResponse(response);

          const book = response.parse();
          s.set("parsedBook", book);

          expect(book.author.firstName).toBe("Patrick");
          expect(book.author.lastName).toBe("Rothfuss");
          expect(book.title).toBe("THE NAME OF THE WIND");
          expect(book.rating).toBe(7);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );

    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `parses stream with nested schema (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const recommendBook = defineCall<{ author: string }>()({
          model,
          maxTokens: 300,
          format,
          template: ({ author }) =>
            `Please recommend the most popular book by ${author}`,
        });

        const snap = await snapshotTest(async (s) => {
          const response = await recommendBook.stream({
            author: "Patrick Rothfuss",
          });
          await response.consume();
          s.setResponse(response);

          const book = response.parse();
          s.set("parsedBook", book);

          expect(book.author.firstName).toBe("Patrick");
          expect(book.author.lastName).toBe("Rothfuss");
          expect(book.title).toBe("THE NAME OF THE WIND");
          expect(book.rating).toBe(7);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );

    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `parses stream with context (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const recommendBook = defineCall<{ ctx: Context<string> }>()({
          model,
          maxTokens: 300,
          format,
          template: ({ ctx }) =>
            `Please recommend the most popular book by ${ctx.deps}`,
        });

        const snap = await snapshotTest(async (s) => {
          const ctx = createContext<string>("Patrick Rothfuss");
          const response = await recommendBook.stream(ctx);
          await response.consume();
          s.setResponse(response);

          const book = response.parse();
          s.set("parsedBook", book);

          expect(book.author.firstName).toBe("Patrick");
          expect(book.author.lastName).toBe("Rothfuss");
          expect(book.title).toBe("THE NAME OF THE WIND");
          expect(book.rating).toBe(7);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );
  });
}
