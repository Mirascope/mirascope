/**
 * Zod-native context example.
 *
 * Demonstrates using context with Zod schema validation for tools.
 * This pattern works WITHOUT the compile-time transformer.
 *
 * Run with: bun run example examples/context/basic-zod.ts
 */
import { llm, type Context } from "mirascope";
import { z } from "zod";

/**
 * A simple library that stores books and their authors.
 */
interface Library {
  books: Record<string, string>; // title -> author
}

/**
 * Tool that looks up a book's author from the library context.
 * Uses Zod validator - no transformer needed!
 */
const getAuthor = llm.defineContextTool({
  name: "get_author",
  description: "Get the author of a book by its title.",
  validator: z.object({
    title: z.string().describe("The title of the book to look up"),
  }),
  // TypeScript infers { title: string } from the validator
  tool: (ctx: Context<Library>, { title }) =>
    ctx.deps.books[title] ?? "Book not found",
});

/**
 * A librarian call that can look up book information.
 */
const librarian = llm.defineCall<{
  ctx: llm.Context<Library>;
  query: string;
}>()({
  model: "openai/gpt-4o-mini",
  tools: [getAuthor],
  template: ({ query }) => query,
});

// Create our library with some books
const library: Library = {
  books: {
    Dune: "Frank Herbert",
    Neuromancer: "William Gibson",
    "The Hobbit": "J.R.R. Tolkien",
  },
};

// Create the context with our library as deps
const ctx = llm.createContext<Library>(library);

// Ask the librarian a question
let response = await librarian(ctx, { query: "Who wrote Neuromancer?" });

// Handle tool calls in a loop until the model responds with text
while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools(ctx);
  response = await response.resume(ctx, toolOutputs);
}

console.log(response.text());
// Neuromancer was written by William Gibson.
