import { describe, expect, it } from 'vitest';
import { MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS } from '@/llm/providers/anthropic/model-info';
import type { AnthropicKnownModels } from '@/llm/providers/anthropic/model-info';

describe('model-info', () => {
  describe('AnthropicKnownModels type', () => {
    it('accepts known model ids', () => {
      const modelId: AnthropicKnownModels = 'anthropic/claude-sonnet-4-5';
      expect(modelId).toBe('anthropic/claude-sonnet-4-5');
    });
  });

  describe('MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS', () => {
    it('is a Set', () => {
      expect(MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS).toBeInstanceOf(Set);
    });

    it('contains older models without strict outputs', () => {
      expect(
        MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS.has('claude-3-opus')
      ).toBe(true);
      expect(
        MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS.has('claude-3-haiku')
      ).toBe(true);
    });

    it('does not contain newer models with strict outputs', () => {
      expect(
        MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS.has('claude-opus-4-5')
      ).toBe(false);
      expect(
        MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS.has('claude-sonnet-4-5')
      ).toBe(false);
    });
  });
});
