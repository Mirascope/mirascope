/**
 * E2E tests for retry stream behavior.
 *
 * Tests streaming retry patterns including StreamRestarted exception handling.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createContext } from "@/llm/context";
import { RetriesExhausted, StreamRestarted } from "@/llm/exceptions";
import { RetryModel, retryModel } from "@/llm/retries/retry-model";
import {
  RetryStreamResponse,
  ContextRetryStreamResponse,
} from "@/llm/retries/retry-stream-responses";

import {
  setupMockProvider,
  teardownMockProvider,
  SERVER_ERROR,
  CONNECTION_ERROR,
  type MockProvider,
} from "./mock-provider";

// Mock sleep to avoid actual delays in tests
vi.mock("@/llm/retries/utils", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/llm/retries/utils")>();
  return {
    ...actual,
    sleep: vi.fn().mockResolvedValue(undefined),
  };
});

describe("RetryModel stream", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  describe("successful streams", () => {
    it("returns RetryStreamResponse", async () => {
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      expect(response).toBeInstanceOf(RetryStreamResponse);
    });

    it("streams text content", async () => {
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");
      const chunks: string[] = [];
      for await (const text of response.textStream()) {
        chunks.push(text);
      }

      expect(chunks.join("")).toBe("mock response");
    });
  });

  describe("stream retry on error", () => {
    it("raises StreamRestarted on retryable error", async () => {
      mockProvider.setStreamExceptions([CONNECTION_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      await expect(async () => {
        for await (const _chunk of response.chunkStream()) {
          // Should throw on first iteration
        }
      }).rejects.toThrow(StreamRestarted);
    });

    it("StreamRestarted contains failure information", async () => {
      mockProvider.setStreamExceptions([CONNECTION_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      try {
        for await (const _chunk of response.chunkStream()) {
          // Should throw
        }
        expect.fail("Should have thrown");
      } catch (e) {
        expect(e).toBeInstanceOf(StreamRestarted);
        const restarted = e as StreamRestarted;
        expect(restarted.failure.exception).toBe(CONNECTION_ERROR);
      }
    });

    it("can continue after catching StreamRestarted", async () => {
      mockProvider.setStreamExceptions([CONNECTION_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      let restartCount = 0;
      let finalText = "";

      while (true) {
        try {
          const chunks: string[] = [];
          for await (const text of response.textStream()) {
            chunks.push(text);
          }
          finalText = chunks.join("");
          break;
        } catch (e) {
          if (e instanceof StreamRestarted) {
            restartCount++;
          } else {
            throw e;
          }
        }
      }

      expect(restartCount).toBe(1);
      expect(finalText).toBe("mock response");
    });

    it("tracks retry failures across restarts", async () => {
      mockProvider.setStreamExceptions([CONNECTION_ERROR, SERVER_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      let restartCount = 0;
      while (true) {
        try {
          for await (const _text of response.textStream()) {
            // Consume stream
          }
          break;
        } catch (e) {
          if (e instanceof StreamRestarted) {
            restartCount++;
          } else {
            throw e;
          }
        }
      }

      expect(restartCount).toBe(2);
      expect(response.retryFailures).toHaveLength(2);
      expect(response.retryFailures[0]?.exception).toBe(CONNECTION_ERROR);
      expect(response.retryFailures[1]?.exception).toBe(SERVER_ERROR);
    });
  });

  describe("stream retry exhaustion", () => {
    it("throws RetriesExhausted when all retries fail", async () => {
      mockProvider.setStreamExceptions([
        CONNECTION_ERROR,
        CONNECTION_ERROR,
        CONNECTION_ERROR,
      ]);
      const model = retryModel("mock/test-model", { maxRetries: 2 });

      const response = await model.stream("Hello");

      // Exhaust all retries
      await expect(async () => {
        while (true) {
          try {
            for await (const _text of response.textStream()) {
              // Consume stream
            }
            break;
          } catch (e) {
            if (e instanceof StreamRestarted) {
              continue;
            }
            throw e;
          }
        }
      }).rejects.toThrow(RetriesExhausted);
    });
  });

  describe("non-retryable stream errors", () => {
    it("throws non-retryable errors immediately", async () => {
      const nonRetryable = new Error("non-retryable");
      mockProvider.setStreamExceptions([nonRetryable]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.stream("Hello");

      await expect(async () => {
        for await (const _chunk of response.chunkStream()) {
          // Should throw
        }
      }).rejects.toBe(nonRetryable);
    });
  });
});

describe("RetryModel contextStream", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns ContextRetryStreamResponse", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const response = await model.contextStream(ctx, "Hello");

    expect(response).toBeInstanceOf(ContextRetryStreamResponse);
  });

  it("streams text content", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const response = await model.contextStream(ctx, "Hello");
    const chunks: string[] = [];
    for await (const text of response.textStream()) {
      chunks.push(text);
    }

    expect(chunks.join("")).toBe("mock response");
  });

  it("raises StreamRestarted on retryable error", async () => {
    mockProvider.setStreamExceptions([SERVER_ERROR]);
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const response = await model.contextStream(ctx, "Hello");

    await expect(async () => {
      for await (const _chunk of response.chunkStream()) {
        // Should throw
      }
    }).rejects.toThrow(StreamRestarted);
  });

  it("can continue after catching StreamRestarted", async () => {
    mockProvider.setStreamExceptions([SERVER_ERROR]);
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const response = await model.contextStream(ctx, "Hello");

    let restartCount = 0;
    while (true) {
      try {
        for await (const _text of response.textStream()) {
          // Consume
        }
        break;
      } catch (e) {
        if (e instanceof StreamRestarted) {
          restartCount++;
        } else {
          throw e;
        }
      }
    }

    expect(restartCount).toBe(1);
  });
});

describe("RetryStreamResponse.executeTools", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns empty array when no tools", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const response = await model.stream("Hello");

    // Consume stream first
    for await (const _text of response.textStream()) {
      // consume
    }

    const result = await response.executeTools();

    expect(result).toEqual([]);
  });
});

describe("RetryStreamResponse.model", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns RetryModel with same config", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 6,
      initialDelay: 1.5,
    });
    const response = await model.stream("Hello");

    const responseModel = await response.model;

    expect(responseModel).toBeInstanceOf(RetryModel);
    expect(responseModel.retryConfig.maxRetries).toBe(6);
    expect(responseModel.retryConfig.initialDelay).toBe(1.5);

    // Consume stream
    for await (const _text of response.textStream()) {
      // consume
    }
  });

  it("exposes retryConfig via getter", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 8,
      initialDelay: 2.5,
    });
    const response = await model.stream("Hello");

    expect(response.retryConfig.maxRetries).toBe(8);
    expect(response.retryConfig.initialDelay).toBe(2.5);

    // Consume stream
    for await (const _text of response.textStream()) {
      // consume
    }
  });
});

describe("RetryStreamResponse.resume", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resumes stream via response method", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const response = await model.stream("Hello");

    // Consume first stream
    for await (const _text of response.textStream()) {
      // consume
    }

    const followUp = await response.resume("Follow up");

    expect(followUp).toBeInstanceOf(RetryStreamResponse);
    // Consume follow-up stream
    for await (const _text of followUp.textStream()) {
      // consume
    }
  });
});

describe("RetryModel stream resume methods", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resumeStream returns RetryStreamResponse", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const initialResponse = await model.call("Hello");

    const followUp = await model.resumeStream(initialResponse, "Follow up");

    expect(followUp).toBeInstanceOf(RetryStreamResponse);
    // Consume stream
    for await (const _text of followUp.textStream()) {
      // consume
    }
  });

  it("resumeStream handles retry errors", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const initialResponse = await model.call("Hello");
    mockProvider.setStreamExceptions([SERVER_ERROR]);

    const followUp = await model.resumeStream(initialResponse, "Follow up");

    let restartCount = 0;
    while (true) {
      try {
        for await (const _text of followUp.textStream()) {
          // consume
        }
        break;
      } catch (e) {
        if (e instanceof StreamRestarted) {
          restartCount++;
        } else {
          throw e;
        }
      }
    }

    expect(restartCount).toBe(1);
  });
});

describe("ContextRetryStreamResponse.resume", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resumes stream via response method", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const initialResponse = await model.contextStream(ctx, "Hello");
    // Consume first stream
    for await (const _text of initialResponse.textStream()) {
      // consume
    }

    const followUp = await initialResponse.resume(ctx, "Follow up");

    expect(followUp).toBeInstanceOf(ContextRetryStreamResponse);
    // Consume follow-up stream
    for await (const _text of followUp.textStream()) {
      // consume
    }
  });

  it("exposes retryConfig via getter", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 5,
      initialDelay: 2.0,
    });
    const ctx = createContext({});
    const response = await model.contextStream(ctx, "Hello");

    expect(response.retryConfig.maxRetries).toBe(5);
    expect(response.retryConfig.initialDelay).toBe(2.0);

    // Consume stream
    for await (const _text of response.textStream()) {
      // consume
    }
  });
});

describe("ContextRetryStreamResponse retry exhaustion", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("throws RetriesExhausted when all context stream retries fail", async () => {
    mockProvider.setStreamExceptions([
      SERVER_ERROR,
      SERVER_ERROR,
      SERVER_ERROR,
    ]);
    const model = retryModel("mock/test-model", { maxRetries: 2 });
    const ctx = createContext({});

    const response = await model.contextStream(ctx, "Hello");

    // Exhaust all retries
    await expect(async () => {
      while (true) {
        try {
          for await (const _text of response.textStream()) {
            // Consume stream
          }
          break;
        } catch (e) {
          if (e instanceof StreamRestarted) {
            continue;
          }
          throw e;
        }
      }
    }).rejects.toThrow(RetriesExhausted);
  });
});

describe("ContextRetryStreamResponse.executeTools", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("executeTools returns empty array when no tools", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});
    const response = await model.contextStream(ctx, "Hello");

    // Consume stream first
    for await (const _text of response.textStream()) {
      // consume
    }

    const result = await response.executeTools(ctx);

    expect(result).toEqual([]);
  });
});
