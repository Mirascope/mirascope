/**
 * Tests for TogetherProvider.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TogetherProvider } from '@/llm/providers/together/provider';

describe('TogetherProvider', () => {
  const originalApiKey = process.env.TOGETHER_API_KEY;

  beforeEach(() => {
    delete process.env.TOGETHER_API_KEY;
  });

  afterEach(() => {
    if (originalApiKey === undefined) {
      delete process.env.TOGETHER_API_KEY;
    } else {
      process.env.TOGETHER_API_KEY = originalApiKey;
    }
  });

  it('initializes with correct id', () => {
    const provider = new TogetherProvider({ apiKey: 'test-key' });
    expect(provider.id).toBe('together');
  });

  it('uses TOGETHER_API_KEY from environment', () => {
    process.env.TOGETHER_API_KEY = 'env-test-key';
    const provider = new TogetherProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('env-test-key');
  });

  it('uses custom api_key from init', () => {
    const provider = new TogetherProvider({ apiKey: 'custom-key' });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('custom-key');
  });

  it('prefers init api_key over environment', () => {
    process.env.TOGETHER_API_KEY = 'env-key';
    const provider = new TogetherProvider({ apiKey: 'init-key' });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('init-key');
  });

  it('uses default base_url', () => {
    const provider = new TogetherProvider({ apiKey: 'test-key' });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      'https://api.together.xyz/v1'
    );
  });

  it('uses custom base_url from init', () => {
    const provider = new TogetherProvider({
      apiKey: 'test-key',
      baseURL: 'https://custom.together.ai/v1',
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      'https://custom.together.ai/v1'
    );
  });

  it('uses model_id as-is for Together API', () => {
    const provider = new TogetherProvider({ apiKey: 'test-key' });
    expect(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      (provider as any).modelName('meta-llama/Llama-3.3-70B-Instruct-Turbo')
    ).toBe('meta-llama/Llama-3.3-70B-Instruct-Turbo');
  });
});
