# Mirascope TypeScript (Alpha)

The TypeScript implementation of Mirascope: a type-safe, ergonomic library for building LLM-powered applications. Like its Python counterpart, Mirascope TypeScript provides a "Goldilocks API" - more control than agent frameworks, more ergonomic than raw provider APIs.

> [!IMPORTANT]
> **Alpha Status**: This is an early release. APIs may change.
> We welcome feedback and contributions!

## Installation

```bash
# Using bun
bun add mirascope@alpha

# Using npm
npm install mirascope@alpha
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

> [!NOTE]
> The transform plugin requires a build tool (Vite, esbuild) or a runtime loader (Node.js `--import`, Bun preload). Environments that run TypeScript directly without custom loader support (e.g., Deno) cannot use the transform plugin — use Zod schemas instead.

### Node.js (Runtime)

For runtime transformation with Node.js 20.6+ (required for `--import` flag support), use the custom ESM loader. The loader handles full TypeScript compilation — no `--experimental-strip-types` needed:

```bash
node --import mirascope/loader your-script.ts

# Or set NODE_OPTIONS
NODE_OPTIONS='--import mirascope/loader' node your-script.ts
```

> [!NOTE]
> Runtime transformation is slower than build-time approaches. For production, use esbuild or Vite plugins instead.

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

### Bun (Runtime)

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

> [!NOTE]
> The preload script is already configured in this package - just run `bun run your-script.ts`.

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

### Deno

Deno's built-in TypeScript support and Node.js compatibility work out of the box:

```bash
deno run --allow-net --allow-env your-script.ts
```

> [!NOTE]
> Deno doesn't support custom TypeScript transformers, so the transform plugin is not available. Use Zod schemas for tools and structured output (`defineTool` with `validator`, `defineFormat` with `validator`, or pass a Zod schema directly as `format`). `defineCall`, `model.call()`, and all Zod-based patterns work directly.

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

## Ops: Instrumentation, Tracing & Versioning

The `ops` module provides observability and versioning for your LLM applications, with automatic integration to Mirascope Cloud or any OpenTelemetry-compatible backend.

### Configuration

```typescript
import { ops } from "mirascope";

// Uses MIRASCOPE_API_KEY environment variable
ops.configure();

// Or explicit API key
ops.configure({ apiKey: "your-api-key" });

// Or custom OpenTelemetry provider
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
ops.configure({ tracerProvider: new NodeTracerProvider() });
```

### Tracing

Wrap functions or calls with `trace()` to create spans:

```typescript
import { llm, ops } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

// Trace a call
const tracedRecommendBook = ops.trace(recommendBook, {
  name: "recommend-book",
  tags: ["recommendation", "books"],
  metadata: { source: "example" },
});

const response = await tracedRecommendBook({ genre: "fantasy" });

// Access span metadata
const result = await tracedRecommendBook.wrapped({ genre: "sci-fi" });
console.log(result.traceId, result.spanId);
```

### Versioning

Track function versions based on closure analysis. Changes to your function code or its dependencies automatically create new versions:

```typescript
import { ops } from "mirascope";

const computeEmbedding = ops.version(
  async (text: string) => {
    // Your embedding logic
    return [0.1, 0.2, 0.3];
  },
  {
    name: "embedding-v1",
    tags: ["embedding", "production"],
  }
);

// Access version info (hash, signatureHash, name, version, tags, metadata)
console.log(computeEmbedding.versionInfo);

// Get wrapped result with span info and annotation support
const result = await computeEmbedding.wrapped("hello");
await result.annotate({ label: "pass" }); // or "fail"
```

> [!NOTE]
> For accurate source-level versioning, use the [Transform Plugin](#transform-plugin). Without it, versioning uses compiled JavaScript via `fn.toString()`.

### Sessions

Group related traces under a session ID:

```typescript
import { ops } from "mirascope";

await ops.session({ id: "user-123-conversation-1" }, async () => {
  const response = await tracedChat({ message: "Hello!" });
  console.log(ops.currentSession()?.id); // "user-123-conversation-1"
});

// With attributes
await ops.session(
  {
    id: "session-2",
    attributes: { userId: "user-456", channel: "web" },
  },
  async () => {
    // Attributes are propagated to spans
  }
);
```

### Spans

Create custom spans for non-LLM operations:

```typescript
import { ops } from "mirascope";

await ops.span("data-processing", async (span) => {
  span.info("Starting processing");
  span.set({ "app.batch_size": 100 });

  // Nested spans
  await ops.span("validation", async (child) => {
    child.debug("Validating input");
  });

  span.info("Complete", { records: 100 });
});
```

### LLM Instrumentation

Automatically instrument all LLM calls with OpenTelemetry GenAI semantic conventions:

```typescript
import { ops } from "mirascope";

ops.instrumentLLM();

// Now all Model calls automatically create spans with:
// - gen_ai.system: "anthropic"
// - gen_ai.request.model: "claude-haiku-4-5"
// - gen_ai.usage.input_tokens / output_tokens
const response = await recommendBook({ genre: "mystery" });

// Check status
console.log(ops.isLLMInstrumented()); // true
ops.uninstrumentLLM();
```

### Context Propagation

Propagate trace context across service boundaries:

```typescript
import { ops } from "mirascope";

// Inject context into outgoing HTTP headers
const headers: Record<string, string> = {};
ops.injectContext(headers);
await fetch(url, { headers });

// Extract context on receiving side
await ops.propagatedContext(incomingHeaders, async () => {
  await ops.span("downstream-work", async (span) => {
    // Linked to upstream trace
  });
});

// Session propagation
const sessionId = ops.extractSessionId(incomingHeaders);
if (sessionId) {
  await ops.session({ id: sessionId }, async () => {
    // Continue session from upstream
  });
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
- `ops/` - Tracing, versioning, sessions, and instrumentation

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
