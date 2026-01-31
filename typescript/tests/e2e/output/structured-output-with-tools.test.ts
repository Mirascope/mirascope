/**
 * E2E tests for structured output combined with tools.
 *
 * Tests verify the flow: call with tools → execute tools → resume → parse structured output.
 */

import { resolve } from "node:path";
import { z } from "zod";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { createContext, type Context } from "@/llm/context";
import { defineFormat, type FormattingMode } from "@/llm/formatting";
import { defineContextTool, defineTool } from "@/llm/tools";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(
  resolve(__dirname, "cassettes"),
  "structured-output-with-tools",
);

/**
 * Mock book database.
 */
const BOOK_DB: Record<string, string> = {
  "0-7653-1178-X":
    "Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
};

/**
 * Book summary schema for structured output.
 */
const BookSummarySchema = z.object({
  title: z.string().describe("The title of the book"),
  author: z.string().describe("The author of the book"),
  pages: z.number().int().describe("Number of pages"),
  publicationYear: z.number().int().describe("Year of publication"),
});

type BookSummary = z.infer<typeof BookSummarySchema>;

/**
 * Tool input schema for ISBN lookup.
 */
const BookLookupSchema = z.object({
  isbn: z.string().describe("The ISBN of the book to look up"),
});

/**
 * Tool to look up book information by ISBN.
 */
const getBookInfo = defineTool({
  name: "get_book_info",
  description: "Look up book information by ISBN.",
  validator: BookLookupSchema,
  tool: ({ isbn }) => {
    return BOOK_DB[isbn] ?? "Book not found";
  },
});

/**
 * Context-aware tool to look up book information.
 * Uses defineContextTool with Zod validator pattern.
 */
const getBookInfoWithContext = defineContextTool({
  name: "get_book_info",
  description: "Look up book information by ISBN.",
  validator: BookLookupSchema,
  tool: (ctx: Context<Record<string, string>>, { isbn }) => {
    return ctx.deps[isbn] ?? "Book not found";
  },
});

/**
 * Providers that support structured output with tools.
 */
const STRUCTURED_OUTPUT_PROVIDERS: ProviderConfig[] = PROVIDERS.filter(
  (p) => p.providerId === "anthropic",
);

/**
 * Helper to create format based on mode.
 */
function createFormat(mode: FormattingMode | null) {
  return mode !== null
    ? defineFormat<BookSummary>({ mode, validator: BookSummarySchema })
    : BookSummarySchema;
}

/**
 * Formatting modes to test.
 */
const MODES: { mode: FormattingMode | null; label: string }[] = [
  { mode: "tool", label: "tool mode" },
  { mode: "json", label: "json mode" },
  { mode: null, label: "default mode" },
];

/**
 * Modes that support streaming with tools.
 * JSON mode has known issues with streaming after tool execution.
 */
const STREAMING_MODES: { mode: FormattingMode | null; label: string }[] = [
  { mode: "tool", label: "tool mode" },
  { mode: null, label: "default mode" },
];

// Non-streaming tests work with all modes
for (const { mode, label } of MODES) {
  const modeSlug = mode ?? "default";
  describe(`structured output with tools (${label})`, () => {
    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `calls tool then parses structured output (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const analyzeBook = defineCall<{ isbn: string }>()({
          model,
          maxTokens: 500,
          tools: [getBookInfo],
          format,
          template: ({ isbn }) =>
            `Please look up the book with ISBN ${isbn} and provide detailed info`,
        });

        const snap = await snapshotTest(async (s) => {
          let response = await analyzeBook({ isbn: "0-7653-1178-X" });

          expect(response.toolCalls.length).toBe(1);
          const toolOutputs = await response.executeTools();

          response = await response.resume(toolOutputs);
          s.setResponse(response);

          const bookSummary = response.parse();
          s.set("parsedBook", bookSummary);

          expect(bookSummary.title).toBe("Mistborn: The Final Empire");
          expect(bookSummary.author).toBe("Brandon Sanderson");
          expect(bookSummary.pages).toBe(544);
          expect(bookSummary.publicationYear).toBe(2006);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );

    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `calls tool with context then parses (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const analyzeBook = defineCall<{
          ctx: Context<Record<string, string>>;
          isbn: string;
        }>()({
          model,
          maxTokens: 500,
          tools: [getBookInfoWithContext],
          format,
          template: ({ isbn }) =>
            `Please look up the book with ISBN ${isbn} and provide detailed info`,
        });

        const snap = await snapshotTest(async (s) => {
          const ctx = createContext<Record<string, string>>(BOOK_DB);
          let response = await analyzeBook(ctx, { isbn: "0-7653-1178-X" });

          expect(response.toolCalls.length).toBe(1);
          const toolOutputs = await response.executeTools(ctx);

          response = await response.resume(ctx, toolOutputs);
          s.setResponse(response);

          const bookSummary = response.parse();
          s.set("parsedBook", bookSummary);

          expect(bookSummary.title).toBe("Mistborn: The Final Empire");
          expect(bookSummary.author).toBe("Brandon Sanderson");
          expect(bookSummary.pages).toBe(544);
          expect(bookSummary.publicationYear).toBe(2006);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );
  });
}

// Streaming tests only work with tool mode and default mode (not JSON mode)
for (const { mode, label } of STREAMING_MODES) {
  const modeSlug = mode ?? "default";
  describe(`structured output with tools streaming (${label})`, () => {
    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `streams tool call then parses structured output (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const analyzeBook = defineCall<{ isbn: string }>()({
          model,
          maxTokens: 500,
          tools: [getBookInfo],
          format,
          template: ({ isbn }) =>
            `Please look up the book with ISBN ${isbn} and provide detailed info`,
        });

        const snap = await snapshotTest(async (s) => {
          let response = await analyzeBook.stream({ isbn: "0-7653-1178-X" });
          await response.consume();

          expect(response.toolCalls.length).toBe(1);
          const toolOutputs = await response.executeTools();

          response = await response.resume(toolOutputs);
          await response.consume();
          s.setResponse(response);

          const bookSummary = response.parse();
          s.set("parsedBook", bookSummary);

          expect(bookSummary.title).toBe("Mistborn: The Final Empire");
          expect(bookSummary.author).toBe("Brandon Sanderson");
          expect(bookSummary.pages).toBe(544);
          expect(bookSummary.publicationYear).toBe(2006);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );

    it.record.each(STRUCTURED_OUTPUT_PROVIDERS)(
      `streams tool call with context then parses (${modeSlug})`,
      async ({ model }) => {
        const format = createFormat(mode);

        const analyzeBook = defineCall<{
          ctx: Context<Record<string, string>>;
          isbn: string;
        }>()({
          model,
          maxTokens: 500,
          tools: [getBookInfoWithContext],
          format,
          template: ({ isbn }) =>
            `Please look up the book with ISBN ${isbn} and provide detailed info`,
        });

        const snap = await snapshotTest(async (s) => {
          const ctx = createContext<Record<string, string>>(BOOK_DB);
          let response = await analyzeBook.stream(ctx, {
            isbn: "0-7653-1178-X",
          });
          await response.consume();

          expect(response.toolCalls.length).toBe(1);
          const toolOutputs = await response.executeTools(ctx);

          response = await response.resume(ctx, toolOutputs);
          await response.consume();
          s.setResponse(response);

          const bookSummary = response.parse();
          s.set("parsedBook", bookSummary);

          expect(bookSummary.title).toBe("Mistborn: The Final Empire");
          expect(bookSummary.author).toBe("Brandon Sanderson");
          expect(bookSummary.pages).toBe(544);
          expect(bookSummary.publicationYear).toBe(2006);
        });

        expect(snap.toObject()).toMatchSnapshot();
      },
    );
  });
}
