import { describe, expect, it } from 'vitest';
import {
  MODELS_WITHOUT_AUDIO_SUPPORT,
  NON_REASONING_MODELS,
  MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
  MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
} from '@/llm/providers/openai/model-info';
import type { OpenAIKnownModels } from '@/llm/providers/openai/model-info';

describe('OpenAIKnownModels type', () => {
  it('accepts known model ID', () => {
    const modelId: OpenAIKnownModels = 'openai/gpt-4o';

    expect(modelId).toBe('openai/gpt-4o');
  });

  it('accepts known model ID with api suffix', () => {
    const modelId: OpenAIKnownModels = 'openai/gpt-4o:responses';

    expect(modelId).toBe('openai/gpt-4o:responses');
  });
});

describe('MODELS_WITHOUT_AUDIO_SUPPORT', () => {
  it('is a ReadonlySet', () => {
    expect(MODELS_WITHOUT_AUDIO_SUPPORT).toBeInstanceOf(Set);
  });

  it('contains model IDs without openai/ prefix', () => {
    for (const modelId of MODELS_WITHOUT_AUDIO_SUPPORT) {
      expect(modelId).not.toMatch(/^openai\//);
    }
  });

  it('can check if a model lacks audio support', () => {
    const hasMethod = typeof MODELS_WITHOUT_AUDIO_SUPPORT.has === 'function';

    expect(hasMethod).toBe(true);
  });
});

describe('NON_REASONING_MODELS', () => {
  it('is a ReadonlySet', () => {
    expect(NON_REASONING_MODELS).toBeInstanceOf(Set);
  });

  it('contains model IDs without openai/ prefix', () => {
    for (const modelId of NON_REASONING_MODELS) {
      expect(modelId).not.toMatch(/^openai\//);
    }
  });

  it('can check if a model is non-reasoning', () => {
    const hasMethod = typeof NON_REASONING_MODELS.has === 'function';

    expect(hasMethod).toBe(true);
  });
});

describe('MODELS_WITHOUT_JSON_SCHEMA_SUPPORT', () => {
  it('is a ReadonlySet', () => {
    expect(MODELS_WITHOUT_JSON_SCHEMA_SUPPORT).toBeInstanceOf(Set);
  });

  it('contains model IDs without openai/ prefix', () => {
    for (const modelId of MODELS_WITHOUT_JSON_SCHEMA_SUPPORT) {
      expect(modelId).not.toMatch(/^openai\//);
    }
  });

  it('can check if a model lacks JSON schema support', () => {
    const hasMethod =
      typeof MODELS_WITHOUT_JSON_SCHEMA_SUPPORT.has === 'function';

    expect(hasMethod).toBe(true);
  });
});

describe('MODELS_WITHOUT_JSON_OBJECT_SUPPORT', () => {
  it('is a ReadonlySet', () => {
    expect(MODELS_WITHOUT_JSON_OBJECT_SUPPORT).toBeInstanceOf(Set);
  });

  it('contains model IDs without openai/ prefix', () => {
    for (const modelId of MODELS_WITHOUT_JSON_OBJECT_SUPPORT) {
      expect(modelId).not.toMatch(/^openai\//);
    }
  });

  it('can check if a model lacks JSON object support', () => {
    const hasMethod =
      typeof MODELS_WITHOUT_JSON_OBJECT_SUPPORT.has === 'function';

    expect(hasMethod).toBe(true);
  });
});
