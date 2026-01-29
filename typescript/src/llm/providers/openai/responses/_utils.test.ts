/**
 * Unit tests for OpenAI Responses provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping and thinking config encoding.
 */

import { describe, it, expect } from 'vitest';
import { user } from '@/llm/messages';
import { Audio, Image } from '@/llm/content';
import { FeatureNotSupportedError } from '@/llm/exceptions';
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

    const params = buildRequestParams(
      'openai/o4-mini:responses',
      messages,
      undefined,
      {
        thinking: { level: 'medium' },
      }
    );

    expect(params.reasoning).toEqual({ effort: 'medium' });
  });

  it('sets reasoning with summary when includeThoughts is true', () => {
    const messages = [user('Hello')];

    const params = buildRequestParams(
      'openai/o4-mini:responses',
      messages,
      undefined,
      {
        thinking: { level: 'high', includeThoughts: true },
      }
    );

    expect(params.reasoning).toEqual({ effort: 'high', summary: 'auto' });
  });
});

describe('image encoding', () => {
  it('encodes URL image source', () => {
    const urlImage = Image.fromUrl('https://example.com/image.png');
    const messages = [user(['Describe this', urlImage])];

    const params = buildRequestParams(
      'openai/gpt-4o:responses',
      messages,
      undefined,
      {}
    );

    // Check that the URL is passed through correctly
    expect(params.input).toContainEqual({
      role: 'user',
      content: [
        { type: 'input_text', text: 'Describe this' },
        {
          type: 'input_image',
          image_url: 'https://example.com/image.png',
          detail: 'auto',
        },
      ],
    });
  });
});

describe('audio encoding', () => {
  it('throws FeatureNotSupportedError for audio input', () => {
    // Create valid WAV audio with proper magic bytes (RIFF....WAVE)
    const wavAudio = Audio.fromBytes(
      new Uint8Array([
        0x52,
        0x49,
        0x46,
        0x46, // 'RIFF'
        0x00,
        0x00,
        0x00,
        0x00, // file size (placeholder)
        0x57,
        0x41,
        0x56,
        0x45, // 'WAVE'
      ])
    );
    const messages = [user(['Listen to this', wavAudio])];

    expect(() =>
      buildRequestParams('openai/gpt-4o:responses', messages, undefined, {})
    ).toThrow(FeatureNotSupportedError);
  });
});
