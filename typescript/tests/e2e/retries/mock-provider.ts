/**
 * Test utilities for retry testing.
 *
 * Provides mock responses and exception injection for testing retry logic.
 */

import { vi } from "vitest";

import type { AssistantMessage, UserMessage } from "@/llm/messages";
import type { FinishReason, Usage } from "@/llm/responses";

import { textStart, textChunk, textEnd } from "@/llm/content/text";
import {
  ConnectionError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from "@/llm/exceptions";
import { Model } from "@/llm/models";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { Response } from "@/llm/responses/response";
import { StreamResponse } from "@/llm/responses/stream-response";

// ===== Predefined Error Instances =====

export const SERVER_ERROR = new ServerError("server error", {
  provider: "mock",
});
export const CONNECTION_ERROR = new ConnectionError("connection failed", {
  provider: "mock",
});
export const RATE_LIMIT_ERROR = new RateLimitError("rate limited", {
  provider: "mock",
});
export const TIMEOUT_ERROR = new TimeoutError("timeout", {
  provider: "mock",
});

/**
 * All default retryable exceptions for testing.
 */
export const DEFAULT_RETRYABLE_EXCEPTIONS: Error[] = [
  SERVER_ERROR,
  CONNECTION_ERROR,
  RATE_LIMIT_ERROR,
  TIMEOUT_ERROR,
];

// ===== Mock Message Helpers =====

function createUserMessage(): UserMessage {
  return {
    role: "user",
    content: [{ type: "text", text: "Hello" }],
    name: null,
  };
}

// ===== Mock Response Creators =====

/**
 * Create a mock Response for testing.
 */
export function createMockResponse(
  modelId = "mock/test-model",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params: any = {},
): Response {
  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content: [{ type: "text", text: "mock response" }],
    name: null,
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    rawMessage: {},
  };

  return new Response({
    raw: {},
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    params,
    inputMessages: [createUserMessage()],
    assistantMessage,
    finishReason: "stop" as FinishReason,
    usage: { inputTokens: 10, outputTokens: 5 } as Usage,
  });
}

/**
 * Create a mock StreamResponse for testing.
 */
export function createMockStreamResponse(
  modelId = "mock/test-model",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params: any = {},
): StreamResponse {
  async function* chunkIterator() {
    yield textStart();
    yield textChunk("mock ");
    yield textChunk("response");
    yield textEnd();
  }

  return new StreamResponse({
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    params,
    inputMessages: [createUserMessage()],
    chunkIterator: chunkIterator(),
  });
}

/**
 * Create a mock ContextResponse for testing.
 */
export function createMockContextResponse<DepsT>(
  modelId = "mock/test-model",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params: any = {},
): ContextResponse<DepsT> {
  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content: [{ type: "text", text: "mock response" }],
    name: null,
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    rawMessage: {},
  };

  return new ContextResponse<DepsT>({
    raw: {},
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    params,
    inputMessages: [createUserMessage()],
    assistantMessage,
    finishReason: "stop" as FinishReason,
    usage: { inputTokens: 10, outputTokens: 5 } as Usage,
  });
}

/**
 * Create a mock ContextStreamResponse for testing.
 */
export function createMockContextStreamResponse<DepsT>(
  modelId = "mock/test-model",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params: any = {},
): ContextStreamResponse<DepsT> {
  async function* chunkIterator() {
    yield textStart();
    yield textChunk("mock ");
    yield textChunk("response");
    yield textEnd();
  }

  return new ContextStreamResponse<DepsT>({
    providerId: "mock",
    modelId,
    providerModelName: "test-model",
    params,
    inputMessages: [createUserMessage()],
    chunkIterator: chunkIterator(),
  });
}

// ===== Mock Provider State =====

export interface MockProvider {
  callCount: number;
  streamCallCount: number;
  setExceptions: (exceptions: Error[]) => void;
  setStreamExceptions: (exceptions: Error[]) => void;
  reset: () => void;
}

let _callCount = 0;
let _streamCallCount = 0;
let _exceptions: Error[] = [];
let _streamExceptions: Error[] = [];
let _currentExceptionIndex = 0;
let _currentStreamExceptionIndex = 0;

/**
 * Set up mock provider by spying on Model methods.
 */
export function setupMockProvider(): MockProvider {
  _callCount = 0;
  _streamCallCount = 0;
  _exceptions = [];
  _streamExceptions = [];
  _currentExceptionIndex = 0;
  _currentStreamExceptionIndex = 0;

  vi.spyOn(Model.prototype, "call").mockImplementation(
    async function (this: Model) {
      _callCount++;
      if (_currentExceptionIndex < _exceptions.length) {
        const exception = _exceptions[_currentExceptionIndex];
        _currentExceptionIndex++;
        if (exception) throw exception;
      }
      return createMockResponse(this.modelId, this.params);
    },
  );

  vi.spyOn(Model.prototype, "stream").mockImplementation(
    async function (this: Model) {
      _streamCallCount++;

      // Create stream that may throw during iteration
      async function* chunkIterator() {
        if (_currentStreamExceptionIndex < _streamExceptions.length) {
          const exception = _streamExceptions[_currentStreamExceptionIndex];
          _currentStreamExceptionIndex++;
          if (exception) throw exception;
        }
        yield textStart();
        yield textChunk("mock ");
        yield textChunk("response");
        yield textEnd();
      }

      return new StreamResponse({
        providerId: "mock",
        modelId: this.modelId,
        providerModelName: "test-model",
        params: this.params,
        inputMessages: [createUserMessage()],
        chunkIterator: chunkIterator(),
      });
    },
  );

  vi.spyOn(Model.prototype, "contextCall").mockImplementation(
    async function (this: Model) {
      _callCount++;
      if (_currentExceptionIndex < _exceptions.length) {
        const exception = _exceptions[_currentExceptionIndex];
        _currentExceptionIndex++;
        if (exception) throw exception;
      }
      return createMockContextResponse(this.modelId, this.params);
    },
  );

  vi.spyOn(Model.prototype, "contextStream").mockImplementation(
    async function (this: Model) {
      _streamCallCount++;

      async function* chunkIterator() {
        if (_currentStreamExceptionIndex < _streamExceptions.length) {
          const exception = _streamExceptions[_currentStreamExceptionIndex];
          _currentStreamExceptionIndex++;
          if (exception) throw exception;
        }
        yield textStart();
        yield textChunk("mock ");
        yield textChunk("response");
        yield textEnd();
      }

      return new ContextStreamResponse({
        providerId: "mock",
        modelId: this.modelId,
        providerModelName: "test-model",
        params: this.params,
        inputMessages: [createUserMessage()],
        chunkIterator: chunkIterator(),
      });
    },
  );

  // Mock resume methods
  vi.spyOn(Model.prototype, "resume").mockImplementation(
    async function (this: Model) {
      _callCount++;
      if (_currentExceptionIndex < _exceptions.length) {
        const exception = _exceptions[_currentExceptionIndex];
        _currentExceptionIndex++;
        if (exception) throw exception;
      }
      return createMockResponse(this.modelId, this.params);
    },
  );

  vi.spyOn(Model.prototype, "resumeStream").mockImplementation(
    async function (this: Model) {
      _streamCallCount++;

      async function* chunkIterator() {
        if (_currentStreamExceptionIndex < _streamExceptions.length) {
          const exception = _streamExceptions[_currentStreamExceptionIndex];
          _currentStreamExceptionIndex++;
          if (exception) throw exception;
        }
        yield textStart();
        yield textChunk("mock ");
        yield textChunk("response");
        yield textEnd();
      }

      return new StreamResponse({
        providerId: "mock",
        modelId: this.modelId,
        providerModelName: "test-model",
        params: this.params,
        inputMessages: [createUserMessage()],
        chunkIterator: chunkIterator(),
      });
    },
  );

  vi.spyOn(Model.prototype, "contextResume").mockImplementation(
    async function (this: Model) {
      _callCount++;
      if (_currentExceptionIndex < _exceptions.length) {
        const exception = _exceptions[_currentExceptionIndex];
        _currentExceptionIndex++;
        if (exception) throw exception;
      }
      return createMockContextResponse(this.modelId, this.params);
    },
  );

  vi.spyOn(Model.prototype, "contextResumeStream").mockImplementation(
    async function (this: Model) {
      _streamCallCount++;

      async function* chunkIterator() {
        if (_currentStreamExceptionIndex < _streamExceptions.length) {
          const exception = _streamExceptions[_currentStreamExceptionIndex];
          _currentStreamExceptionIndex++;
          if (exception) throw exception;
        }
        yield textStart();
        yield textChunk("mock ");
        yield textChunk("response");
        yield textEnd();
      }

      return new ContextStreamResponse({
        providerId: "mock",
        modelId: this.modelId,
        providerModelName: "test-model",
        params: this.params,
        inputMessages: [createUserMessage()],
        chunkIterator: chunkIterator(),
      });
    },
  );

  return {
    get callCount() {
      return _callCount;
    },
    get streamCallCount() {
      return _streamCallCount;
    },
    setExceptions(exceptions: Error[]) {
      _exceptions = [...exceptions];
      _currentExceptionIndex = 0;
    },
    setStreamExceptions(exceptions: Error[]) {
      _streamExceptions = [...exceptions];
      _currentStreamExceptionIndex = 0;
    },
    reset() {
      _callCount = 0;
      _streamCallCount = 0;
      _exceptions = [];
      _streamExceptions = [];
      _currentExceptionIndex = 0;
      _currentStreamExceptionIndex = 0;
    },
  };
}

/**
 * Clean up mock provider.
 */
export function teardownMockProvider(): void {
  vi.restoreAllMocks();
  _callCount = 0;
  _streamCallCount = 0;
  _exceptions = [];
  _streamExceptions = [];
  _currentExceptionIndex = 0;
  _currentStreamExceptionIndex = 0;
}
