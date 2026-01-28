/**
 * Unit tests for Anthropic provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error cases and encoding logic that can't be tested via API calls.
 */

import { describe, it, expect } from 'vitest';
import { user } from '@/llm/messages';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import { Audio, Image } from '@/llm/content';
import { buildRequestParams, computeThinkingBudget } from './_utils';

describe('computeThinkingBudget', () => {
  it('returns 0 for none level (disabled)', () => {
    expect(computeThinkingBudget('none', 4096)).toBe(0);
  });

  it('returns -1 for default level (provider default)', () => {
    expect(computeThinkingBudget('default', 4096)).toBe(-1);
  });

  it('returns minimum 1024 for minimal level', () => {
    // minimal has multiplier 0, but minimum is 1024
    expect(computeThinkingBudget('minimal', 4096)).toBe(1024);
  });

  it('computes budget based on multiplier for low level', () => {
    // low has multiplier 0.2
    expect(computeThinkingBudget('low', 10000)).toBe(2000);
  });

  it('computes budget based on multiplier for medium level', () => {
    // medium has multiplier 0.4
    expect(computeThinkingBudget('medium', 10000)).toBe(4000);
  });

  it('computes budget based on multiplier for high level', () => {
    // high has multiplier 0.6
    expect(computeThinkingBudget('high', 10000)).toBe(6000);
  });

  it('computes budget based on multiplier for max level', () => {
    // max has multiplier 0.8
    expect(computeThinkingBudget('max', 10000)).toBe(8000);
  });

  it('enforces minimum 1024 tokens', () => {
    // With small maxTokens, budget would be less than 1024
    expect(computeThinkingBudget('low', 1000)).toBe(1024);
  });
});

describe('buildRequestParams', () => {
  it('throws FeatureNotSupportedError when both temperature and topP specified', () => {
    const messages = [user('Hello')];

    expect(() =>
      buildRequestParams('anthropic/claude-haiku-4-5', messages, {
        temperature: 0.7,
        topP: 0.9,
      })
    ).toThrow(FeatureNotSupportedError);
  });

  describe('thinking config encoding', () => {
    it('sets thinking disabled when level is none', () => {
      const messages = [user('Hello')];

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        {
          thinking: { level: 'none' },
        }
      );

      expect(params.thinking).toEqual({ type: 'disabled' });
    });

    it('sets thinking enabled with budget when level is specified', () => {
      const messages = [user('Hello')];

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        {
          thinking: { level: 'medium' },
          maxTokens: 10000,
        }
      );

      // medium = 0.4 multiplier, 10000 * 0.4 = 4000
      expect(params.thinking).toEqual({
        type: 'enabled',
        budget_tokens: 4000,
      });
    });

    it('does not set thinking when level is default', () => {
      const messages = [user('Hello')];

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        {
          thinking: { level: 'default' },
        }
      );

      // Default means don't set thinking parameter
      expect(params.thinking).toBeUndefined();
    });
  });

  describe('image encoding', () => {
    it('throws FeatureNotSupportedError for HEIC image format', () => {
      // Create a minimal HEIC image (using magic bytes)
      // HEIC files start with 'ftyp' at offset 4 with 'heic' brand
      const heicMagicBytes = new Uint8Array([
        0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x69, 0x63,
      ]);
      const heicImage = Image.fromBytes(heicMagicBytes);
      const messages = [user(['Check this image', heicImage])];

      expect(() =>
        buildRequestParams('anthropic/claude-haiku-4-5', messages, {})
      ).toThrow(FeatureNotSupportedError);
    });

    it('throws FeatureNotSupportedError for HEIF image format', () => {
      // HEIF files also use 'ftyp' but with 'mif1' brand
      const heifMagicBytes = new Uint8Array([
        0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, 0x6d, 0x69, 0x66, 0x31,
      ]);
      const heifImage = Image.fromBytes(heifMagicBytes);
      const messages = [user(['Check this image', heifImage])];

      expect(() =>
        buildRequestParams('anthropic/claude-haiku-4-5', messages, {})
      ).toThrow(FeatureNotSupportedError);
    });
  });

  describe('audio encoding', () => {
    it('throws FeatureNotSupportedError for audio input', () => {
      // MP3 magic bytes (ID3 tag with padding to meet 12-byte minimum)
      const mp3MagicBytes = new Uint8Array([
        0x49,
        0x44,
        0x33, // 'ID3'
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00, // padding
      ]);
      const audio = Audio.fromBytes(mp3MagicBytes);
      const messages = [user(['Transcribe this', audio])];

      expect(() =>
        buildRequestParams('anthropic/claude-haiku-4-5', messages, {})
      ).toThrow(FeatureNotSupportedError);
    });
  });
});
