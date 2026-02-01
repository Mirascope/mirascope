/**
 * Unit tests for Google provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping and thinking config encoding.
 */

import { describe, it, expect } from 'vitest';
import {
  AuthenticationError,
  PermissionError,
  NotFoundError,
  RateLimitError,
  BadRequestError,
  ServerError,
  APIError,
  FeatureNotSupportedError,
} from '@/llm/exceptions';
import { Image } from '@/llm/content';
import { user } from '@/llm/messages';
import {
  mapGoogleErrorByStatus,
  computeGoogleThinkingConfig,
  buildRequestParams,
} from './_utils';

describe('mapGoogleErrorByStatus', () => {
  it('maps 401 to AuthenticationError', () => {
    expect(mapGoogleErrorByStatus(401)).toBe(AuthenticationError);
  });

  it('maps 403 to PermissionError', () => {
    expect(mapGoogleErrorByStatus(403)).toBe(PermissionError);
  });

  it('maps 404 to NotFoundError', () => {
    expect(mapGoogleErrorByStatus(404)).toBe(NotFoundError);
  });

  it('maps 429 to RateLimitError', () => {
    expect(mapGoogleErrorByStatus(429)).toBe(RateLimitError);
  });

  it('maps 400 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(400)).toBe(BadRequestError);
  });

  it('maps 422 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(422)).toBe(BadRequestError);
  });

  it('maps 5xx to ServerError', () => {
    expect(mapGoogleErrorByStatus(500)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(502)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(503)).toBe(ServerError);
  });

  it('maps unknown status codes to APIError', () => {
    expect(mapGoogleErrorByStatus(418)).toBe(APIError);
    expect(mapGoogleErrorByStatus(499)).toBe(APIError);
  });
});

describe('computeGoogleThinkingConfig', () => {
  describe('Gemini 2.5 models (budget-based)', () => {
    const modelId = 'google/gemini-2.5-flash';

    it('returns dynamic budget (-1) for default level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'default' },
        8192,
        modelId
      );
      expect(config.thinkingBudget).toBe(-1);
    });

    it('returns 0 budget for none level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'none' },
        8192,
        modelId
      );
      expect(config.thinkingBudget).toBe(0);
    });

    it('computes budget based on multiplier for medium level', () => {
      // medium has multiplier 0.4
      const config = computeGoogleThinkingConfig(
        { level: 'medium' },
        10000,
        modelId
      );
      expect(config.thinkingBudget).toBe(4000);
    });

    it('sets includeThoughts when specified', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'medium', includeThoughts: true },
        8192,
        modelId
      );
      expect(config.includeThoughts).toBe(true);
    });
  });

  describe('Gemini 3 Flash models (level-based)', () => {
    const modelId = 'google/gemini-3-flash';

    it('returns MINIMAL for minimal level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'minimal' },
        8192,
        modelId
      );
      expect(config.thinkingLevel).toBe('MINIMAL');
    });

    it('returns MEDIUM for medium level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'medium' },
        8192,
        modelId
      );
      expect(config.thinkingLevel).toBe('MEDIUM');
    });
  });

  describe('Gemini 3 Pro models (level-based, LOW/HIGH only)', () => {
    const modelId = 'google/gemini-3-pro';

    it('returns LOW for low level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'low' },
        8192,
        modelId
      );
      expect(config.thinkingLevel).toBe('LOW');
    });

    it('returns HIGH for high level', () => {
      const config = computeGoogleThinkingConfig(
        { level: 'high' },
        8192,
        modelId
      );
      expect(config.thinkingLevel).toBe('HIGH');
    });
  });
});

describe('buildRequestParams thinking config', () => {
  it('sets thinkingConfig when thinking is specified', () => {
    const messages = [user('Hello')];

    const params = buildRequestParams(
      'google/gemini-2.5-flash',
      messages,
      undefined,
      {
        thinking: { level: 'medium' },
        maxTokens: 10000,
      }
    );

    expect(params.config?.thinkingConfig).toEqual({
      thinkingBudget: 4000, // medium = 0.4 multiplier
    });
  });
});

describe('image encoding', () => {
  it('throws FeatureNotSupportedError for URL image source', () => {
    const urlImage = Image.fromUrl('https://example.com/image.png');
    const messages = [user(['Check this image', urlImage])];

    expect(() =>
      buildRequestParams('google/gemini-2.5-flash', messages, undefined, {})
    ).toThrow(FeatureNotSupportedError);
  });
});
