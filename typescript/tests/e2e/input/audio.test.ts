/**
 * E2E tests for audio content in messages.
 *
 * Tests verify that audio is correctly encoded and sent to providers.
 *
 * Note: Audio is only supported by:
 * - Google (all formats)
 * - OpenAI Completions API (wav/mp3 only, and only specific models like gpt-audio)
 *
 * Anthropic and OpenAI Responses API do NOT support audio inputs.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { defineCall } from '@/llm/calls';
import { user } from '@/llm/messages';
import { Audio } from '@/llm/content';
import type { ProviderConfig } from '@/tests/e2e/providers';

const it = createIt(resolve(__dirname, 'cassettes'), 'audio');

// Path to test audio
const TAGLINE_AUDIO_PATH = resolve(__dirname, '../assets/audio/tagline.mp3');

/**
 * Providers that support audio inputs.
 */
const AUDIO_PROVIDERS: ProviderConfig[] = [
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
  // OpenAI audio support requires gpt-4o-audio-preview model
  {
    providerId: 'openai:completions',
    model: 'openai/gpt-4o-audio-preview:completions',
  },
];

/**
 * Load the test audio as base64.
 */
function loadTestAudio(): Audio {
  const data = readFileSync(TAGLINE_AUDIO_PATH);
  return Audio.fromBytes(new Uint8Array(data));
}

describe('audio content', () => {
  it.record.each(AUDIO_PROVIDERS)(
    'encodes audio content',
    async ({ model }) => {
      const audio = loadTestAudio();
      const call = defineCall({
        model,
        maxTokens: 200,
        template: () => [
          user([
            'What is being said in this audio? Transcribe it exactly.',
            audio,
          ]),
        ],
      });

      const response = await call();

      // Response should transcribe the audio
      expect(response.text().length).toBeGreaterThan(0);
    }
  );
});
