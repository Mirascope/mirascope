import { describe, expect, it } from 'vitest';
import { modelName } from '@/llm/providers/openai/model-id';
import type { OpenAIModelId, ApiMode } from '@/llm/providers/openai/model-id';

describe('modelName', () => {
  it('extracts model name and appends responses mode', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o';
    const apiMode: ApiMode = 'responses';

    expect(modelName(modelId, apiMode)).toBe('gpt-4o:responses');
  });

  it('extracts model name and appends completions mode', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o';
    const apiMode: ApiMode = 'completions';

    expect(modelName(modelId, apiMode)).toBe('gpt-4o:completions');
  });

  it('returns base name when apiMode is null', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o';

    expect(modelName(modelId, null)).toBe('gpt-4o');
  });

  it('strips existing :responses suffix before appending mode', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o:responses';

    expect(modelName(modelId, 'completions')).toBe('gpt-4o:completions');
  });

  it('strips existing :completions suffix before appending mode', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o:completions';

    expect(modelName(modelId, 'responses')).toBe('gpt-4o:responses');
  });

  it('strips existing suffix when apiMode is null', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o:responses';

    expect(modelName(modelId, null)).toBe('gpt-4o');
  });

  it('handles model without openai/ prefix', () => {
    const modelId: OpenAIModelId = 'gpt-4o';

    expect(modelName(modelId, 'responses')).toBe('gpt-4o:responses');
  });

  it('handles model without prefix and null apiMode', () => {
    const modelId: OpenAIModelId = 'gpt-4o';

    expect(modelName(modelId, null)).toBe('gpt-4o');
  });
});

describe('OpenAIModelId type', () => {
  it('accepts known model IDs', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o';

    expect(modelId).toBe('openai/gpt-4o');
  });

  it('accepts known model IDs with api suffix', () => {
    const modelId: OpenAIModelId = 'openai/gpt-4o:responses';

    expect(modelId).toBe('openai/gpt-4o:responses');
  });

  it('accepts custom string model IDs', () => {
    const modelId: OpenAIModelId = 'openai/my-custom-model';

    expect(modelId).toBe('openai/my-custom-model');
  });
});

describe('ApiMode type', () => {
  it('accepts responses mode', () => {
    const mode: ApiMode = 'responses';

    expect(mode).toBe('responses');
  });

  it('accepts completions mode', () => {
    const mode: ApiMode = 'completions';

    expect(mode).toBe('completions');
  });
});
