/**
 * Unit tests for Anthropic provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error cases that can't be tested via successful API calls.
 */

import { describe, it, expect } from 'vitest';
import { user } from '@/llm/messages';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import { buildRequestParams } from './_utils';

describe('buildRequestParams error handling', () => {
  it('throws FeatureNotSupportedError when both temperature and topP specified', () => {
    const messages = [user('Hello')];

    expect(() =>
      buildRequestParams('anthropic/claude-haiku-4-5', messages, {
        temperature: 0.7,
        topP: 0.9,
      })
    ).toThrow(FeatureNotSupportedError);
  });
});
