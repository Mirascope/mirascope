/**
 * Unit tests for OpenAI Responses provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping and thinking config encoding.
 */

import { describe, it, expect } from 'vitest';
import { user } from '@/llm/messages';
import { computeReasoning, buildRequestParams } from './_utils';

describe('computeReasoning', () => {
  it('maps default level to medium effort', () => {
    expect(computeReasoning('default', false)).toEqual({ effort: 'medium' });
  });

  it('maps none level to none effort', () => {
    expect(computeReasoning('none', false)).toEqual({ effort: 'none' });
  });

  it('maps minimal level to minimal effort', () => {
    expect(computeReasoning('minimal', false)).toEqual({ effort: 'minimal' });
  });

  it('maps low level to low effort', () => {
    expect(computeReasoning('low', false)).toEqual({ effort: 'low' });
  });

  it('maps medium level to medium effort', () => {
    expect(computeReasoning('medium', false)).toEqual({ effort: 'medium' });
  });

  it('maps high level to high effort', () => {
    expect(computeReasoning('high', false)).toEqual({ effort: 'high' });
  });

  it('maps max level to xhigh effort', () => {
    expect(computeReasoning('max', false)).toEqual({ effort: 'xhigh' });
  });

  it('adds summary when includeThoughts is true', () => {
    expect(computeReasoning('medium', true)).toEqual({
      effort: 'medium',
      summary: 'auto',
    });
  });
});

describe('buildRequestParams thinking config', () => {
  it('sets reasoning when thinking is specified', () => {
    const messages = [user('Hello')];

    const params = buildRequestParams('openai/o4-mini:responses', messages, {
      thinking: { level: 'medium' },
    });

    expect(params.reasoning).toEqual({ effort: 'medium' });
  });

  it('sets reasoning with summary when includeThoughts is true', () => {
    const messages = [user('Hello')];

    const params = buildRequestParams('openai/o4-mini:responses', messages, {
      thinking: { level: 'high', includeThoughts: true },
    });

    expect(params.reasoning).toEqual({ effort: 'high', summary: 'auto' });
  });
});
