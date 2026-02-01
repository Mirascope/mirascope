/**
 * Custom vitest wrapper with Polly.js integration.
 *
 * Provides `it.record` for tests that need HTTP recording/playback.
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { it as vitestIt, describe, expect } from 'vitest';
import { Polly } from '@pollyjs/core';
import Persister, { type Har } from '@pollyjs/persister';
import FetchAdapter from '@pollyjs/adapter-fetch';
import { resetProviderRegistry } from '@/llm/providers/registry';
import { ProviderConfig } from '@/tests/e2e/providers';

// Register adapter
Polly.register(FetchAdapter);

interface FlatFSPersisterOptions {
  recordingsDir: string;
}

/**
 * Custom persister that stores recordings as flat .har files.
 * e.g., cassettes/my-test-name.har instead of cassettes/my-test-name_hash/recording.har
 */
class FlatFSPersister extends Persister<FlatFSPersisterOptions> {
  static override get id() {
    return 'flat-fs';
  }

  override readonly defaultOptions: FlatFSPersisterOptions = {
    recordingsDir: './recordings',
  };

  private filePath(recordingId: string): string {
    // Strip the hash suffix (e.g., "test-name_12345" -> "test-name")
    const name = recordingId.replace(/_\d+$/, '');
    return join(this.options.recordingsDir, `${name}.har`);
  }

  override onFindRecording(recordingId: string): Promise<Har | null> {
    const filePath = this.filePath(recordingId);
    if (existsSync(filePath)) {
      return Promise.resolve(
        JSON.parse(readFileSync(filePath, 'utf-8')) as Har
      );
    }
    return Promise.resolve(null);
  }

  override onSaveRecording(recordingId: string, data: unknown): Promise<void> {
    const filePath = this.filePath(recordingId);
    mkdirSync(dirname(filePath), { recursive: true });
    writeFileSync(filePath, JSON.stringify(data, null, 2));
    return Promise.resolve();
  }

  override onDeleteRecording(_recordingId: string): Promise<void> {
    // Not needed for our use case
    return Promise.resolve();
  }
}

Polly.register(FlatFSPersister);

// Re-export for convenience
export { describe, expect };

const SENSITIVE_HEADERS = [
  'authorization',
  'x-api-key',
  'x-goog-api-key',
  'anthropic-organization-id',
  'cookie',
];

/**
 * Converts a test name to a valid recording name.
 * Replaces spaces and special characters with hyphens.
 */
function toRecordingName(testName: string): string {
  return testName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Creates a Polly instance for a test.
 */
function createPolly(recordingName: string, cassettesDir: string): Polly {
  const polly = new Polly(recordingName, {
    adapters: ['fetch'],
    persister: 'flat-fs',
    persisterOptions: {
      'flat-fs': {
        recordingsDir: cassettesDir,
      },
    },
    recordIfMissing: true,
    recordFailedRequests: true,
    flushRequestsOnStop: true,
    matchRequestsBy: {
      headers: false,
      body: true,
      order: false,
    },
  });

  // Sanitize sensitive headers in recordings
  polly.server.any().on('beforePersist', (_req, recording) => {
    const requestHeaders = (
      recording as {
        request?: { headers?: Array<{ name: string; value: string }> };
      }
    ).request?.headers;
    if (requestHeaders) {
      for (const header of requestHeaders) {
        if (SENSITIVE_HEADERS.includes(header.name.toLowerCase())) {
          header.value = '[REDACTED]';
        }
      }
    }
  });

  return polly;
}

type RecordTestFn = (
  name: string,
  fn: () => Promise<void>,
  timeout?: number
) => void;

type ParameterizedTestFn<T> = (
  name: string,
  fn: (config: T) => Promise<void>,
  timeout?: number
) => void;

interface RecordIt extends RecordTestFn {
  skip: RecordTestFn;
  only: RecordTestFn;
  /**
   * Run the same test for each provider configuration.
   * Cassettes are namespaced by provider.
   *
   * @example
   * ```typescript
   * it.record.each(PROVIDERS)('encodes system message', async ({ model }) => {
   *   const call = defineCall({ model, ... });
   *   const response = await call();
   *   expect(response.text().length).toBeGreaterThan(0);
   * });
   * ```
   */
  each: (providers: ProviderConfig[]) => ParameterizedTestFn<ProviderConfig>;
}

/**
 * Creates a wrapped test function that automatically manages Polly lifecycle.
 */
function createRecordTestFn(
  cassettesDir: string,
  namespace: string,
  original: typeof vitestIt
): RecordTestFn {
  return (name: string, fn: () => Promise<void>, timeout?: number) => {
    original(
      name,
      async () => {
        const recordingName = toRecordingName(name);
        const namespacedDir = join(cassettesDir, namespace);
        const polly = createPolly(recordingName, namespacedDir);
        resetProviderRegistry();
        try {
          await fn();
        } finally {
          await polly.stop();
          resetProviderRegistry();
        }
      },
      timeout
    );
  };
}

/**
 * Creates a parameterized test function that runs for each provider.
 */
function createRecordEachFn(
  cassettesDir: string,
  namespace: string,
  original: typeof vitestIt
): (providers: ProviderConfig[]) => ParameterizedTestFn<ProviderConfig> {
  return (providers: ProviderConfig[]) => {
    return (
      name: string,
      fn: (config: ProviderConfig) => Promise<void>,
      timeout?: number
    ) => {
      for (const provider of providers) {
        const testName = `[${provider.providerId}] ${name}`;
        original(
          testName,
          async () => {
            const recordingName = toRecordingName(name);
            // Namespace by both test category and provider
            const namespacedDir = join(
              cassettesDir,
              namespace,
              provider.providerId
            );
            const polly = createPolly(recordingName, namespacedDir);
            resetProviderRegistry();
            try {
              await fn(provider);
            } finally {
              await polly.stop();
              resetProviderRegistry();
            }
          },
          timeout
        );
      }
    };
  };
}

/**
 * Creates a custom `it` with `it.record` for HTTP recording tests.
 *
 * @param cassettesDir - Directory to store cassette recordings
 * @param namespace - Subdirectory for this test file's cassettes (e.g., 'call')
 * @returns Custom `it` with `.record` method
 *
 * @example
 * ```typescript
 * import { resolve } from 'path';
 * import { createIt, describe, expect } from '@/tests/e2e/utils';
 *
 * const it = createIt(resolve(__dirname, 'cassettes'), 'call');
 *
 * describe('my e2e tests', () => {
 *   it.record('makes an API call', async () => {
 *     const response = await myApiCall();
 *     expect(response.text()).toMatchInlineSnapshot();
 *   });
 * });
 * ```
 */
export function createIt(cassettesDir: string, namespace: string) {
  const recordIt: RecordIt = Object.assign(
    createRecordTestFn(cassettesDir, namespace, vitestIt),
    {
      skip: createRecordTestFn(
        cassettesDir,
        namespace,
        vitestIt.skip as typeof vitestIt
      ),
      only: createRecordTestFn(
        cassettesDir,
        namespace,
        vitestIt.only as typeof vitestIt
      ),
      each: createRecordEachFn(cassettesDir, namespace, vitestIt),
    }
  );

  return new Proxy(vitestIt, {
    get(target, prop) {
      if (prop === 'record') {
        return recordIt;
      }
      return Reflect.get(target, prop) as unknown;
    },
  }) as typeof vitestIt & { record: RecordIt };
}
