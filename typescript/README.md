# Mirascope TypeScript (Alpha)

The TypeScript implementation of Mirascope: a type-safe, ergonomic library for building LLM-powered applications. Like its Python counterpart, Mirascope TypeScript provides a "Goldilocks API" - more control than agent frameworks, more ergonomic than raw provider APIs.

> [!IMPORTANT]
> **Alpha Status**: This is an early release. APIs may change.
> We welcome feedback and contributions!

## Installation

```bash
# Using bun
bun add mirascope

# Using npm
npm install mirascope
```

## Quickstart

```typescript
import { llm } from "mirascope";

// Simple call
const model = llm.model("anthropic/claude-haiku-4-5")
const response = await model.call("What's the best way to learn TypeScript?");
console.log(response.text());

// Streaming
const stream = await model.stream("Tell me a joke");
for await (const text of stream.textStream()) {
  process.stdout.write(text);
}
```

## Defining Calls

Use `defineCall` to create reusable, type-safe call functions:

```typescript
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

const response = await recommendBook({ genre: "fantasy" });
console.log(response.text());

// Streaming
const stream = await recommendBook.stream({ genre: "sci-fi" });
for await (const text of stream.textStream()) {
  process.stdout.write(text);
}
```

## Structured Output

> [!NOTE]
> TypeScript interface patterns (non-Zod) require a compile-time transform. See [Transform Plugin](#transform-plugin) for setup instructions.

### With Zod Schema

```typescript
import { llm } from "mirascope";
import { z } from "zod";

const BookSchema = z.object({
  title: z.string().describe("The book title"),
  author: z.string().describe("The author's name"),
  year: z.number().int().describe("Publication year"),
});
type Book = z.infer<typeof BookSchema>;

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  format: BookSchema,
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

const response = await recommendBook({ genre: "mystery" });
const book: Book = response.parse();
console.log(`${book.title} by ${book.author} (${book.year})`);
```

### With TypeScript Interface

```typescript
import { llm } from "mirascope";

/**
 * A book recommendation.
 */
type Book = {
  /** The book title */
  title: string;
  /** The author's name */
  author: string;
  /** Publication year */
  year: number;
};

const recommendBook = llm.defineCall<{ genre: string }, Book>({
  model: "anthropic/claude-haiku-4-5",
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

const response = await recommendBook({ genre: "mystery" });
const book: Book = response.parse();
console.log(`${book.title} by ${book.author} (${book.year})`);
```

## Tools

> [!NOTE]
> TypeScript interface patterns (non-Zod) require a compile-time transform. See [Transform Plugin](#transform-plugin) for setup instructions.

### With Zod Schema

```typescript
import { llm } from "mirascope";
import { z } from "zod";

const getWeather = llm.defineTool({
  name: "get_weather",
  description: "Get the current weather for a location",
  validator: z.object({
    city: z.string().describe("The city name"),
    units: z.enum(["celsius", "fahrenheit"]).default("celsius"),
  }),
  tool: ({ city, units }) => {
    return { city, temperature: 22, units };
  },
});

const assistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [getWeather],
  template: ({ query }) => query,
});

let response = await assistant({ query: "What's the weather in Tokyo?" });

// Execute tools and resume until no more tool calls
while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools();
  response = await response.resume(toolOutputs);
}

console.log(response.text());
```

### With TypeScript Interface

```typescript
import { llm } from "mirascope";

/**
 * Arguments for the weather tool.
 */
type WeatherArgs = {
  /** The city name */
  city: string;
  /** Temperature units */
  units: "celsius" | "fahrenheit";
};

const getWeather = llm.defineTool<WeatherArgs>({
  name: "get_weather",
  description: "Get the current weather for a location",
  tool: ({ city, units }) => {
    return { city, temperature: 22, units };
  },
});

const assistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [getWeather],
  template: ({ query }) => query,
});

let response = await assistant({ query: "What's the weather in Tokyo?" });

while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools();
  response = await response.resume(toolOutputs);
}

console.log(response.text());
```

## Context

Share dependencies (like databases, APIs, etc.) with your tools using context:

```typescript
import { llm, type Context } from "mirascope";
import { z } from "zod";

interface AppDeps {
  db: { getUser: (id: string) => { name: string } };
}

const getUserInfo = llm.defineContextTool({
  name: "get_user",
  description: "Look up user information",
  validator: z.object({
    userId: z.string().describe("The user ID to look up"),
  }),
  tool: (ctx: Context<AppDeps>, { userId }) => {
    return ctx.deps.db.getUser(userId);
  },
});

const assistant = llm.defineCall<{ ctx: Context<AppDeps>; query: string }>()({
  model: "openai/gpt-4o-mini",
  tools: [getUserInfo],
  template: ({ query }) => query,
});

const ctx = llm.createContext<AppDeps>({ db: myDatabase });
let response = await assistant(ctx, { query: "Tell me about user 123" });

while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools(ctx);
  response = await response.resume(ctx, toolOutputs);
}
```

## Provider Configuration

### Custom API Keys

```typescript
import { llm } from "mirascope";

// Use a different API key
llm.registerProvider("openai", { apiKey: "sk-my-key" });

// Or a custom endpoint
llm.registerProvider("anthropic", { baseURL: "https://my-proxy.example.com" });
```

### OpenAI-Compatible Providers

Route any OpenAI-compatible provider through the OpenAI adapter:

```typescript
import { llm } from "mirascope";

// Route grok/ models through xAI's OpenAI-compatible endpoint
llm.registerProvider("openai", {
  scope: "grok/",
  baseURL: "https://api.x.ai/v1",
  apiKey: process.env.XAI_API_KEY,
});

const response = await llm.model("grok/grok-4-latest").call("Hello!");
```

## Transform Plugin

The transform plugin extracts type information from TypeScript interfaces at compile time, enabling the native TypeScript patterns (without Zod) for tools and structured output. This is **optional** - you can use Zod schemas without any build configuration.

### Vite

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import { mirascope } from "mirascope/vite";

export default defineConfig({
  plugins: [mirascope()],
});
```

### esbuild

```typescript
import * as esbuild from "esbuild";
import { mirascope } from "mirascope/esbuild";

await esbuild.build({
  entryPoints: ["src/index.ts"],
  bundle: true,
  outfile: "dist/bundle.js",
  plugins: [mirascope()],
});
```

### Bun

Bun supports a preload script that applies the transform at runtime:

```typescript
// preload.ts
import { mirascope } from "mirascope/bun";
mirascope();
```

```toml
# bunfig.toml
preload = ["./preload.ts"]
```

Now `bun run your-script.ts` will automatically apply the transform.

Alternatively, for production builds, use esbuild:

```typescript
// build.ts
import { mirascope } from "mirascope/esbuild";

await Bun.build({
  entrypoints: ["src/index.ts"],
  outdir: "dist",
  plugins: [mirascope()],
});
```

## Error Handling

```typescript
import { llm } from "mirascope";

try {
  const response = await llm.model("openai/gpt-4o").call("Hello");
} catch (e) {
  if (e instanceof llm.AuthenticationError) {
    console.log("Invalid API key");
  } else if (e instanceof llm.RateLimitError) {
    console.log("Rate limited - try again later");
  } else if (e instanceof llm.MirascopeError) {
    console.log("LLM error:", e.message);
  }
}
```

## Supported Providers

- **Anthropic**: `anthropic/claude-sonnet-4-5`, `anthropic/claude-haiku-4-5`, etc.
- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4o-mini`, etc.
- **Google**: `google/gemini-2.0-flash`, `google/gemini-2.5-pro`, etc.
- **Ollama**: `ollama/llama3.2`, etc. (local models)
- **Together**: `together/meta-llama/...`, etc.
- Any OpenAI-compatible provider via `registerProvider`

## Development Setup

1. **Clone and install**:
   ```bash
   cd typescript
   bun install
   ```

2. **Environment variables** (for e2e tests):
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

3. **Commands**:
   ```bash
   bun run typecheck    # Type checking
   bun run lint         # Linting + formatting
   bun run test         # Run tests
   bun run test:coverage # Tests with coverage (requires 100%)
   ```

## Examples

See the [`examples/`](./examples) directory for more examples:

- `calls/` - Basic and advanced call patterns
- `tools/` - Tool definition and execution
- `format/` - Structured output with Zod
- `streaming/` - Streaming responses
- `context/` - Sharing dependencies with context
- `chaining/` - Chaining and parallel calls
- `reliability/` - Retry and fallback patterns

Run an example:
```bash
bun run example examples/calls/basic.ts
```

## Contributing

We welcome contributions! Please ensure:

1. `bun run typecheck` passes
2. `bun run lint` passes
3. `bun run test:coverage` shows 100% coverage

For more info, see [the contributing page in our docs](https://mirascope.com/docs/contributing).
