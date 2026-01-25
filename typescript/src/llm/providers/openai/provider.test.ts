/**
 * Unit tests for OpenAI provider router.
 *
 * Tests API mode routing and error handling.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OpenAIProvider } from './provider';
import { user } from '@/llm/messages';
import { FeatureNotSupportedError } from '@/llm/exceptions';

// Mock the OpenAI SDK
vi.mock('openai', async (importOriginal) => {
  const actual = await importOriginal<typeof import('openai')>();
  const mockCreate = vi.fn();

  // Create a mock class that mimics OpenAI client
  const MockOpenAI = vi.fn().mockImplementation(() => ({
    chat: {
      completions: {
        create: mockCreate,
      },
    },
  }));

  // Attach the error classes to the mock
  Object.assign(MockOpenAI, {
    AuthenticationError: actual.default.AuthenticationError,
    PermissionDeniedError: actual.default.PermissionDeniedError,
    BadRequestError: actual.default.BadRequestError,
    NotFoundError: actual.default.NotFoundError,
    RateLimitError: actual.default.RateLimitError,
    InternalServerError: actual.default.InternalServerError,
    APIError: actual.default.APIError,
    APIConnectionError: actual.default.APIConnectionError,
    APIConnectionTimeoutError: actual.default.APIConnectionTimeoutError,
    UnprocessableEntityError: actual.default.UnprocessableEntityError,
    ConflictError: actual.default.ConflictError,
  });

  return {
    ...actual,
    default: MockOpenAI,
  };
});

describe('OpenAIProvider', () => {
  let provider: OpenAIProvider;
  let mockCreate: ReturnType<typeof vi.fn>;

  const mockResponse = {
    id: 'chatcmpl-123',
    object: 'chat.completion',
    created: 1677652288,
    model: 'gpt-4o',
    choices: [
      {
        index: 0,
        message: {
          role: 'assistant',
          content: 'Hello!',
        },
        finish_reason: 'stop',
      },
    ],
    usage: {
      prompt_tokens: 5,
      completion_tokens: 2,
      total_tokens: 7,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    provider = new OpenAIProvider({ apiKey: 'test-key' });
    // Get the mock function from the provider's completions provider client
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    mockCreate = (provider as any).completionsProvider.client.chat.completions
      .create;
  });

  describe('constructor', () => {
    it('accepts custom baseURL', () => {
      const customProvider = new OpenAIProvider({
        apiKey: 'test-key',
        baseURL: 'https://custom.api.example.com',
      });
      expect(customProvider.id).toBe('openai');
    });
  });

  describe('API mode routing', () => {
    it('routes to completions API by default', async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: 'openai/gpt-4o',
        messages: [user('Hi')],
      });

      expect(response.text()).toBe('Hello!');
      expect(mockCreate).toHaveBeenCalled();
    });

    it('routes to completions API with :completions suffix', async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      const response = await provider.call({
        modelId: 'openai/gpt-4o:completions',
        messages: [user('Hi')],
      });

      expect(response.text()).toBe('Hello!');
      expect(mockCreate).toHaveBeenCalled();
    });

    it('throws FeatureNotSupportedError for :responses suffix', async () => {
      await expect(
        provider.call({
          modelId: 'openai/gpt-4o:responses',
          messages: [user('Hi')],
        })
      ).rejects.toThrow(FeatureNotSupportedError);
    });

    it('includes helpful message when responses API not supported', async () => {
      try {
        await provider.call({
          modelId: 'openai/gpt-4o:responses',
          messages: [user('Hi')],
        });
        expect.fail('Expected error to be thrown');
      } catch (e) {
        expect(e).toBeInstanceOf(FeatureNotSupportedError);
        expect((e as FeatureNotSupportedError).message).toContain(
          'not yet supported'
        );
        expect((e as FeatureNotSupportedError).message).toContain(
          ':completions'
        );
      }
    });
  });

  describe('call', () => {
    it('passes params to completions provider', async () => {
      mockCreate.mockResolvedValueOnce(mockResponse);

      await provider.call({
        modelId: 'openai/gpt-4o',
        messages: [user('Hi')],
        params: { temperature: 0.5 },
      });

      expect(mockCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          temperature: 0.5,
        })
      );
    });
  });
});
