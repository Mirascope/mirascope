import { describe, expect, it } from 'vitest';
import { KNOWN_PROVIDER_IDS } from '@/llm/providers/provider-id';
import type { KnownProviderId, ProviderId } from '@/llm/providers/provider-id';

describe('provider-id', () => {
  describe('KNOWN_PROVIDER_IDS', () => {
    it('contains anthropic', () => {
      expect(KNOWN_PROVIDER_IDS).toContain('anthropic');
    });

    it('is a readonly array', () => {
      expect(Array.isArray(KNOWN_PROVIDER_IDS)).toBe(true);
    });
  });

  describe('KnownProviderId type', () => {
    it('accepts known provider ids', () => {
      const anthropic: KnownProviderId = 'anthropic';
      expect(anthropic).toBe('anthropic');
    });
  });

  describe('ProviderId type', () => {
    it('accepts known provider ids', () => {
      const anthropic: ProviderId = 'anthropic';
      expect(anthropic).toBe('anthropic');
    });

    it('accepts custom provider ids', () => {
      const custom: ProviderId = 'my-custom-provider';
      expect(custom).toBe('my-custom-provider');
    });
  });
});
