/**
 * Mirascope LLM exception hierarchy for unified error handling across providers.
 */

import type { ModelId, ProviderId } from "@/llm/providers";
import type { RetryFailure } from "@/llm/retries/utils";

/**
 * Base exception for all Mirascope LLM errors.
 */
export class MirascopeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

/**
 * Options for constructing a ProviderError.
 */
export interface ProviderErrorOptions {
  provider: ProviderId;
  originalException?: Error | null;
}

/**
 * Base class for errors that originate from a provider SDK.
 *
 * This wraps exceptions from provider libraries (OpenAI, Anthropic, etc.)
 * and provides a unified interface for error handling.
 */
export class ProviderError extends MirascopeError {
  /**
   * The provider that raised this error.
   */
  readonly provider: ProviderId;

  /**
   * The original exception from the provider SDK, if available.
   */
  readonly originalException: Error | null;

  constructor(message: string, options: ProviderErrorOptions) {
    super(message);
    this.provider = options.provider;
    this.originalException = options.originalException ?? null;
    if (this.originalException !== null) {
      this.cause = this.originalException;
    }
  }
}

/**
 * Options for constructing an APIError.
 */
export interface APIErrorOptions extends ProviderErrorOptions {
  statusCode?: number | null;
}

/**
 * Base class for HTTP-level API errors.
 */
export class APIError extends ProviderError {
  /**
   * The HTTP status code, if available.
   */
  readonly statusCode: number | null;

  constructor(message: string, options: APIErrorOptions) {
    super(message, options);
    this.statusCode = options.statusCode ?? null;
  }
}

/**
 * Raised for authentication failures (401, invalid API keys).
 */
export class AuthenticationError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 401 });
  }
}

/**
 * Raised for permission/authorization failures (403).
 */
export class PermissionError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 403 });
  }
}

/**
 * Raised for malformed requests (400, 422).
 */
export class BadRequestError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 400 });
  }
}

/**
 * Raised when requested resource is not found (404).
 */
export class NotFoundError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 404 });
  }
}

/**
 * Raised when rate limits are exceeded (429).
 */
export class RateLimitError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 429 });
  }
}

/**
 * Raised for server-side errors (500+).
 */
export class ServerError extends APIError {
  constructor(message: string, options: APIErrorOptions) {
    super(message, { ...options, statusCode: options.statusCode ?? 500 });
  }
}

/**
 * Raised when unable to connect to the API (network issues, timeouts).
 */
export class ConnectionError extends ProviderError {
  constructor(message: string, options: ProviderErrorOptions) {
    super(message, options);
  }
}

/**
 * Raised when requests timeout or deadline exceeded.
 */
export class TimeoutError extends ProviderError {
  constructor(message: string, options: ProviderErrorOptions) {
    super(message, options);
  }
}

/**
 * Raised when API response fails validation.
 *
 * This wraps the APIResponseValidationErrors that OpenAI and Anthropic both return.
 */
export class ResponseValidationError extends ProviderError {
  constructor(message: string, options: ProviderErrorOptions) {
    super(message, options);
  }
}

/**
 * Base class for errors that occur during tool execution.
 */
export class ToolError extends MirascopeError {}

/**
 * Raised if an uncaught exception is thrown while executing a tool.
 */
export class ToolExecutionError extends ToolError {
  /**
   * The exception that was thrown while executing the tool.
   */
  readonly toolException: Error;

  constructor(toolException: Error | string) {
    let exception: Error;
    let message: string;

    if (typeof toolException === "string") {
      // Support string for snapshot reconstruction
      message = toolException;
      exception = new Error(message);
    } else {
      message = toolException.message;
      exception = toolException;
    }

    super(message);
    this.toolException = exception;
    this.cause = exception;
  }
}

/**
 * Raised if a tool call does not match any registered tool.
 */
export class ToolNotFoundError extends ToolError {
  /**
   * The name of the tool that was not found.
   */
  readonly toolName: string;

  constructor(toolName: string) {
    super(`Tool '${toolName}' not found in registered tools`);
    this.toolName = toolName;
  }
}

/**
 * Raised when response.parse() fails to parse the response content.
 *
 * This wraps errors from JSON extraction, JSON parsing, Pydantic validation,
 * or custom OutputParser functions.
 */
export class ParseError extends MirascopeError {
  /**
   * The original exception that caused the parse failure.
   */
  readonly originalException: Error;

  constructor(message: string, originalException: Error) {
    super(message);
    this.originalException = originalException;
    this.cause = originalException;
  }

  /**
   * Generate a message suitable for retrying with the LLM.
   *
   * Returns a user-friendly message describing what went wrong,
   * suitable for including in a retry prompt.
   */
  retryMessage(): string {
    const original = this.originalException;

    // Check for JSON syntax errors
    if (original instanceof SyntaxError && original.message.includes("JSON")) {
      return (
        "Your response could not be parsed because no valid JSON object " +
        "was found. Please ensure your response contains a JSON object " +
        "with opening '{' and closing '}' braces."
      );
    }

    // Default message for other errors
    return (
      `Your response could not be parsed: ${original.message}\n\n` +
      "Please ensure your response matches the expected format."
    );
  }
}

/**
 * Raised if a Mirascope feature is unsupported by chosen provider.
 *
 * If compatibility is model-specific, then `modelId` should be specified.
 * If the feature is not supported by the provider at all, then it may be `null`.
 */
export class FeatureNotSupportedError extends MirascopeError {
  /**
   * The provider that does not support this feature.
   */
  readonly providerId: ProviderId;

  /**
   * The model that does not support this feature, if model-specific.
   */
  readonly modelId: ModelId | null;

  /**
   * The name of the unsupported feature.
   */
  readonly feature: string;

  constructor(
    feature: string,
    providerId: ProviderId,
    modelId: ModelId | null = null,
    message: string | null = null,
  ) {
    const defaultMessage =
      message ??
      `Feature '${feature}' is not supported by provider '${providerId}'${
        modelId !== null ? ` for model '${modelId}'` : ""
      }`;
    super(defaultMessage);
    this.feature = feature;
    this.providerId = providerId;
    this.modelId = modelId;
  }
}

/**
 * Raised when no provider is registered for a given model_id.
 */
export class NoRegisteredProviderError extends MirascopeError {
  /**
   * The model ID that has no registered provider.
   */
  readonly modelId: string;

  constructor(modelId: string) {
    const message =
      `No provider registered for model '${modelId}'. ` +
      `Use llm.registerProvider() to register a provider for this model.`;
    super(message);
    this.modelId = modelId;
  }
}

/**
 * Raised when no API key is available for a provider.
 *
 * This error is raised during auto-registration when the required API key
 * environment variable is not set. If a Mirascope fallback is available,
 * the error message will suggest using MIRASCOPE_API_KEY as an alternative.
 */
export class MissingAPIKeyError extends MirascopeError {
  /**
   * The provider that requires an API key.
   */
  readonly providerId: string;

  /**
   * The environment variable that should contain the API key.
   */
  readonly envVar: string;

  constructor(
    providerId: string,
    envVar: string,
    hasMirascopeFallback: boolean = false,
  ) {
    let message: string;
    if (hasMirascopeFallback) {
      message =
        `No API key found for ${providerId}. Either:\n` +
        `  1. Set ${envVar} environment variable, or\n` +
        `  2. Set MIRASCOPE_API_KEY for cross-provider support ` +
        `via Mirascope Router\n` +
        `     (Learn more: https://mirascope.com/docs/router)`;
    } else {
      message =
        `No API key found for ${providerId}. ` +
        `Set the ${envVar} environment variable.`;
    }
    super(message);
    this.providerId = providerId;
    this.envVar = envVar;
  }
}

// ===== Retry Exceptions =====

/**
 * Raised when all retry attempts (including fallback models) have been exhausted.
 *
 * This exception preserves the full failure history, allowing users to inspect
 * what went wrong at each attempt.
 *
 * @example
 * ```typescript
 * try {
 *   const response = await retryModel.call("Tell me a story");
 * } catch (e) {
 *   if (e instanceof llm.RetriesExhausted) {
 *     console.log(`Failed after ${e.failures.length} attempts:`);
 *     for (const failure of e.failures) {
 *       console.log(`  - ${failure.model.modelId}: ${failure.exception.message}`);
 *     }
 *   }
 * }
 * ```
 */
export class RetriesExhausted extends MirascopeError {
  /**
   * All failed attempts, in order. The last failure triggered exhaustion.
   */
  readonly failures: RetryFailure[];

  constructor(failures: RetryFailure[]) {
    const uniqueModelNames = [...new Set(failures.map((f) => f.model.modelId))];
    const message =
      `All retries exhausted after ${failures.length} attempt(s) ` +
      `across models: ${JSON.stringify(uniqueModelNames)}`;
    super(message);
    this.failures = failures;
    // Chain to the last error for standard traceback behavior
    const lastFailure = failures[failures.length - 1];
    if (lastFailure !== undefined) {
      this.cause = lastFailure.exception;
    }
  }
}

/**
 * Raised when a stream restarts due to a retryable error.
 *
 * This exception signals that the stream encountered an error and has been
 * reset for a retry attempt. Users should catch this exception and re-iterate
 * the response to continue streaming from the new attempt.
 *
 * @example
 * ```typescript
 * const response = await retryModel.stream("Tell me a story");
 *
 * while (true) {
 *   try {
 *     for await (const text of response.textStream()) {
 *       process.stdout.write(text);
 *     }
 *     break; // Success
 *   } catch (e) {
 *     if (e instanceof llm.StreamRestarted) {
 *       console.log(`Stream restarted: ${e.message}`);
 *       // Loop continues, re-iterates the response
 *     } else {
 *       throw e;
 *     }
 *   }
 * }
 * ```
 */
export class StreamRestarted extends MirascopeError {
  /**
   * The failure that triggered the restart.
   */
  readonly failure: RetryFailure;

  constructor(failure: RetryFailure) {
    const message = `Stream restarted due to: ${failure.exception.message}`;
    super(message);
    this.failure = failure;
    this.cause = failure.exception;
  }
}
