/**
 * Tests for OllamaProvider.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { OllamaProvider } from './provider';

describe('OllamaProvider', () => {
  const originalApiKey = process.env.OLLAMA_API_KEY;
  const originalBaseUrl = process.env.OLLAMA_BASE_URL;

  beforeEach(() => {
    delete process.env.OLLAMA_API_KEY;
    delete process.env.OLLAMA_BASE_URL;
  });

  afterEach(() => {
    if (originalApiKey === undefined) {
      delete process.env.OLLAMA_API_KEY;
    } else {
      process.env.OLLAMA_API_KEY = originalApiKey;
    }
    if (originalBaseUrl === undefined) {
      delete process.env.OLLAMA_BASE_URL;
    } else {
      process.env.OLLAMA_BASE_URL = originalBaseUrl;
    }
  });

  it('initializes with correct id', () => {
    const provider = new OllamaProvider();
    expect(provider.id).toBe('ollama');
  });

  it('uses default "ollama" api_key', () => {
    const provider = new OllamaProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('ollama');
  });

  it('uses OLLAMA_API_KEY from environment', () => {
    process.env.OLLAMA_API_KEY = 'env-test-key';
    const provider = new OllamaProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('env-test-key');
  });

  it('uses custom api_key from init', () => {
    const provider = new OllamaProvider({ apiKey: 'custom-key' });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe('custom-key');
  });

  it('uses default base_url', () => {
    const provider = new OllamaProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe('http://localhost:11434/v1/');
  });

  it('uses OLLAMA_BASE_URL from environment', () => {
    process.env.OLLAMA_BASE_URL = 'http://remote-ollama:11434/v1/';
    const provider = new OllamaProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      'http://remote-ollama:11434/v1/'
    );
  });

  it('uses custom base_url from init', () => {
    const provider = new OllamaProvider({
      baseURL: 'http://custom.ollama.local:11434/v1/',
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      'http://custom.ollama.local:11434/v1/'
    );
  });

  it('strips ollama/ prefix from model_id', () => {
    const provider = new OllamaProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).modelName('ollama/gemma3:4b')).toBe('gemma3:4b');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).modelName('gemma3:4b')).toBe('gemma3:4b');
  });
});
