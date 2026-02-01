/**
 * Basic context example - Transformer-based pattern.
 *
 * Demonstrates using context to share dependencies (like a database)
 * between the call and its tools. Uses JSDoc comments for field descriptions.
 *
 * Run with: bun run example examples/context/basic.ts
 */
import { llm } from "mirascope";

/**
 * A simple library that stores books and their authors.
 */
interface Library {
  books: Record<string, string>; // title -> author
}

/**
 * Arguments for looking up a book's author.
 */
type GetAuthorArgs = {
  /** The title of the book to look up */
  title: string;
};

/**
 * Tool that looks up a book's author from the library context.
 */
const getAuthor = llm.defineContextTool<GetAuthorArgs, Library>({
  name: "get_author",
  description: "Get the author of a book by its title.",
  tool: (ctx, { title }) => ctx.deps.books[title] ?? "Book not found",
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
let response = await librarian(ctx, { query: "Who wrote Dune?" });

// Handle tool calls in a loop until the model responds with text
while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools(ctx);
  response = await response.resume(ctx, toolOutputs);
}

console.log(response.text());
// Dune was written by Frank Herbert.
