/**
 * Type declarations for optional instrumentation packages.
 *
 * These are minimal type stubs for the optional instrumentation packages
 * that may or may not be installed by users.
 */

declare module "@opentelemetry/instrumentation-openai" {
  import type { TracerProvider } from "@opentelemetry/api";

  export class OpenAIInstrumentation {
    instrument(config?: { tracerProvider?: TracerProvider }): void;
    disable(): void;
  }
}

declare module "@traceloop/instrumentation-anthropic" {
  import type { TracerProvider } from "@opentelemetry/api";

  export class AnthropicInstrumentation {
    instrument(config?: { tracerProvider?: TracerProvider }): void;
    disable(): void;
  }
}

declare module "@traceloop/instrumentation-google-generativeai" {
  import type { TracerProvider } from "@opentelemetry/api";

  export class GoogleGenerativeAIInstrumentation {
    instrument(config?: { tracerProvider?: TracerProvider }): void;
    disable(): void;
  }
}
