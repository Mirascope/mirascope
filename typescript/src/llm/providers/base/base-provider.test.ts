/**
 * Tests for BaseProvider error wrapping.
 */

import { describe, it, expect } from 'vitest';
import { createContext, type Context } from '@/llm/context';
import { user, type Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ProviderId } from '@/llm/providers/provider-id';
import { Response } from '@/llm/responses';
import { ContextResponse } from '@/llm/responses/context-response';
import { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import { StreamResponse } from '@/llm/responses/stream-response';
import { APIError, ProviderError } from '@/llm/exceptions';
import {
  BaseProvider,
  type ProviderErrorMap,
} from '@/llm/providers/base/base-provider';

// Custom test error classes
class TestSDKError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'TestSDKError';
    this.status = status;
  }
}

class TestAPIError extends Error {
  statusCode: number;
  constructor(message: string, statusCode: number) {
    super(message);
    this.name = 'TestAPIError';
    this.statusCode = statusCode;
  }
}

// Custom Mirascope error for testing
class TestProviderError extends ProviderError {}
class TestMirascopeAPIError extends APIError {}

// Concrete test provider implementation
class TestProvider extends BaseProvider {
  readonly id: ProviderId = 'anthropic';

  protected readonly errorMap: ProviderErrorMap = [
    [TestAPIError, TestMirascopeAPIError],
    [TestSDKError, TestProviderError],
  ];

  private errorToThrow: Error | null = null;

  setErrorToThrow(error: Error | null): void {
    this.errorToThrow = error;
  }

  protected _call(_args: {
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<Response> {
    if (this.errorToThrow) {
      return Promise.reject(this.errorToThrow);
    }
    return Promise.reject(new Error('Not implemented for tests'));
  }

  protected _stream(_args: {
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<StreamResponse> {
    if (this.errorToThrow) {
      return Promise.reject(this.errorToThrow);
    }
    return Promise.reject(new Error('Not implemented for tests'));
  }

  protected _contextCall<DepsT>(_args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    if (this.errorToThrow) {
      return Promise.reject(this.errorToThrow);
    }
    return Promise.reject(new Error('Not implemented for tests'));
  }

  protected _contextStream<DepsT>(_args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    if (this.errorToThrow) {
      return Promise.reject(this.errorToThrow);
    }
    return Promise.reject(new Error('Not implemented for tests'));
  }

  protected getErrorStatus(e: Error): number | undefined {
    if (e instanceof TestAPIError) {
      return e.statusCode;
    }
    if (e instanceof TestSDKError) {
      return e.status;
    }
    return undefined;
  }
}

describe('BaseProvider', () => {
  describe('call()', () => {
    it('wraps SDK errors in Mirascope error types', async () => {
      const provider = new TestProvider();
      provider.setErrorToThrow(new TestSDKError('Rate limited', 429));

      await expect(
        provider.call({
          modelId: 'test-model',
          messages: [user('Hi')],
        })
      ).rejects.toThrow(TestProviderError);
    });

    it('wraps API errors with status code', async () => {
      const provider = new TestProvider();
      provider.setErrorToThrow(new TestAPIError('Not found', 404));

      try {
        await provider.call({
          modelId: 'test-model',
          messages: [user('Hi')],
        });
        expect.fail('Should have thrown');
      } catch (e) {
        expect(e).toBeInstanceOf(TestMirascopeAPIError);
        expect((e as TestMirascopeAPIError).statusCode).toBe(404);
      }
    });

    it('returns unknown errors as-is', async () => {
      const provider = new TestProvider();
      const unknownError = new Error('Unknown error');
      provider.setErrorToThrow(unknownError);

      await expect(
        provider.call({
          modelId: 'test-model',
          messages: [user('Hi')],
        })
      ).rejects.toBe(unknownError);
    });

    it('wraps non-Error values in Error', async () => {
      const provider = new TestProvider();
      // Force a non-Error throw by using a custom implementation
      provider['_call'] = () => {
        // eslint-disable-next-line @typescript-eslint/only-throw-error
        throw 'string error';
      };

      await expect(
        provider.call({
          modelId: 'test-model',
          messages: [user('Hi')],
        })
      ).rejects.toThrow('string error');
    });
  });

  describe('contextCall()', () => {
    it('wraps SDK errors in Mirascope error types', async () => {
      const provider = new TestProvider();
      provider.setErrorToThrow(new TestSDKError('Rate limited', 429));

      await expect(
        provider.contextCall({
          ctx: createContext({}),
          modelId: 'test-model',
          messages: [user('Hi')],
        })
      ).rejects.toThrow(TestProviderError);
    });
  });

  describe('contextStream()', () => {
    it('wraps SDK errors in Mirascope error types', async () => {
      const provider = new TestProvider();
      provider.setErrorToThrow(new TestSDKError('Rate limited', 429));

      await expect(
        provider.contextStream({
          ctx: createContext({}),
          modelId: 'test-model',
          messages: [user('Hi')],
        })
      ).rejects.toThrow(TestProviderError);
    });
  });
});
