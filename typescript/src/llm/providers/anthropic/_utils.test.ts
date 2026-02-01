/**
 * Unit tests for Anthropic provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error cases and encoding logic that can't be tested via API calls.
 */

import { describe, it, expect } from 'vitest';
import type { Message as AnthropicMessage } from '@anthropic-ai/sdk/resources/messages';
import { user } from '@/llm/messages';
import type { AssistantMessage } from '@/llm/messages';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import { Audio, Image } from '@/llm/content';
import {
  defineFormat,
  FORMAT_TOOL_NAME,
  TOOL_MODE_INSTRUCTIONS,
} from '@/llm/formatting';
import { defineTool } from '@/llm/tools';
import {
  buildRequestParams,
  computeThinkingBudget,
  decodeResponse,
  encodeMessages,
} from './_utils';

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
      buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        undefined,
        undefined,
        {
          temperature: 0.7,
          topP: 0.9,
        }
      )
    ).toThrow(FeatureNotSupportedError);
  });

  describe('thinking config encoding', () => {
    it('sets thinking disabled when level is none', () => {
      const messages = [user('Hello')];

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        undefined,
        undefined,
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
        undefined,
        undefined,
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
        undefined,
        undefined,
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
        buildRequestParams(
          'anthropic/claude-haiku-4-5',
          messages,
          undefined,
          undefined,
          {}
        )
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
        buildRequestParams(
          'anthropic/claude-haiku-4-5',
          messages,
          undefined,
          undefined,
          {}
        )
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
        buildRequestParams(
          'anthropic/claude-haiku-4-5',
          messages,
          undefined,
          undefined,
          {}
        )
      ).toThrow(FeatureNotSupportedError);
    });
  });
});

describe('format encoding', () => {
  it('adds format tool when format mode is tool', () => {
    const messages = [user('Recommend a book')];

    const format = defineFormat({
      mode: 'tool',
      __schema: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          author: { type: 'string' },
        },
        required: ['title', 'author'],
        additionalProperties: false,
      },
    });

    const params = buildRequestParams(
      'anthropic/claude-haiku-4-5',
      messages,
      undefined,
      format,
      {}
    );

    // Should have the format tool
    expect(params.tools).toHaveLength(1);
    expect(params.tools?.[0]?.name).toBe(FORMAT_TOOL_NAME);

    // Should force the format tool via tool_choice
    expect(params.tool_choice).toEqual({
      type: 'tool',
      name: FORMAT_TOOL_NAME,
      disable_parallel_tool_use: true,
    });
  });

  it('adds formatting instructions to system prompt for tool mode', () => {
    const messages = [user('Recommend a book')];

    const format = defineFormat({
      mode: 'tool',
      __schema: {
        type: 'object',
        properties: { title: { type: 'string' } },
        required: ['title'],
        additionalProperties: false,
      },
    });

    const params = buildRequestParams(
      'anthropic/claude-haiku-4-5',
      messages,
      undefined,
      format,
      {}
    );

    // System prompt should be an array with cache_control
    expect(params.system).toEqual([
      {
        type: 'text',
        text: TOOL_MODE_INSTRUCTIONS,
        cache_control: { type: 'ephemeral' },
      },
    ]);
  });

  it('uses type: any when format tool is combined with other tools', () => {
    const messages = [user('Search and recommend a book')];

    const format = defineFormat({
      mode: 'tool',
      __schema: {
        type: 'object',
        properties: { title: { type: 'string' } },
        required: ['title'],
        additionalProperties: false,
      },
    });

    const searchTool = defineTool({
      name: 'search',
      description: 'Search for books',
      tool: () => 'results',
      __schema: {
        type: 'object',
        properties: { query: { type: 'string' } },
        required: ['query'],
        additionalProperties: false,
      },
    });

    const params = buildRequestParams(
      'anthropic/claude-haiku-4-5',
      messages,
      [searchTool],
      format,
      {}
    );

    // Should have both tools
    expect(params.tools).toHaveLength(2);
    const toolNames = params.tools?.map((t) => t.name);
    expect(toolNames).toContain('search');
    expect(toolNames).toContain(FORMAT_TOOL_NAME);

    // Should use 'any' tool_choice to allow either tool
    expect(params.tool_choice).toEqual({ type: 'any' });
  });

  it('throws FeatureNotSupportedError for strict mode', () => {
    const messages = [user('Hello')];

    // Create a format with strict mode manually
    const format = defineFormat({
      mode: 'tool',
      __schema: {
        type: 'object',
        properties: {},
        required: [],
        additionalProperties: false,
      },
    });
    // Override mode to strict (this would normally come from defineFormat with mode: 'strict')
    (format as { mode: string }).mode = 'strict';

    expect(() =>
      buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        undefined,
        format,
        {}
      )
    ).toThrow(FeatureNotSupportedError);
  });
});

describe('raw message round-tripping', () => {
  // Mock response for testing
  const mockAnthropicResponse = {
    id: 'msg_123',
    type: 'message',
    role: 'assistant',
    content: [{ type: 'text', text: 'Hello!' }],
    model: 'claude-haiku-4-5',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: {
      input_tokens: 10,
      output_tokens: 5,
    },
  } as unknown as AnthropicMessage;

  it('decodeResponse stores serialized message in rawMessage', () => {
    const { assistantMessage } = decodeResponse(
      mockAnthropicResponse,
      'anthropic/claude-haiku-4-5'
    );

    // rawMessage should be an object with role and content
    expect(typeof assistantMessage.rawMessage).toBe('object');

    const rawMessage = assistantMessage.rawMessage as unknown as {
      role: string;
      content: Array<Record<string, unknown>>;
    };
    expect(rawMessage.role).toBe('assistant');
    expect(Array.isArray(rawMessage.content)).toBe(true);
    expect(rawMessage.content[0]).toHaveProperty('type', 'text');
    expect(rawMessage.content[0]).toHaveProperty('text', 'Hello!');
  });

  it('decodeResponse sets providerModelName from modelName', () => {
    const { assistantMessage } = decodeResponse(
      mockAnthropicResponse,
      'anthropic/claude-haiku-4-5'
    );

    // Should be the base model name (without provider prefix)
    expect(assistantMessage.providerModelName).toBe('claude-haiku-4-5');
  });

  it('encodeMessages reuses rawMessage for matching assistant messages', () => {
    // Create an assistant message that would have come from decodeResponse
    const assistantMsg: AssistantMessage = {
      role: 'assistant',
      content: [{ type: 'text', text: 'Hello!' }],
      name: null,
      providerId: 'anthropic',
      modelId: 'anthropic/claude-haiku-4-5',
      providerModelName: 'claude-haiku-4-5',
      rawMessage: {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
      } as unknown as AssistantMessage['rawMessage'],
    };

    const messages = [user('Hi'), assistantMsg, user('How are you?')];
    const { messages: encoded } = encodeMessages(
      messages,
      'anthropic/claude-haiku-4-5'
    );

    // Should have: user message, raw assistant message, user message
    expect(encoded).toHaveLength(3);

    // First is user message
    expect(encoded[0]).toEqual({ role: 'user', content: 'Hi' });

    // Second should be the raw message reused directly
    expect(encoded[1]).toHaveProperty('role', 'assistant');
    expect(encoded[1]).toHaveProperty('content');
    expect((encoded[1] as { content: unknown[] }).content[0]).toHaveProperty(
      'type',
      'text'
    );

    // Third is user message - with cache_control because this is multi-turn
    expect(encoded[2]).toEqual({
      role: 'user',
      content: [
        {
          type: 'text',
          text: 'How are you?',
          cache_control: { type: 'ephemeral' },
        },
      ],
    });
  });

  it('encodeMessages does NOT reuse rawMessage for different provider', () => {
    // Create an assistant message from a different provider
    const assistantMsg: AssistantMessage = {
      role: 'assistant',
      content: [{ type: 'text', text: 'Hello!' }],
      name: null,
      providerId: 'openai', // Different provider
      modelId: 'openai/gpt-4o',
      providerModelName: 'gpt-4o',
      rawMessage: {
        role: 'assistant',
        content: 'Hello!',
      } as unknown as AssistantMessage['rawMessage'],
    };

    const messages = [user('Hi'), assistantMsg];
    const { messages: encoded } = encodeMessages(
      messages,
      'anthropic/claude-haiku-4-5'
    );

    // Should encode from content, not raw message
    // Last message in multi-turn gets cache_control
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: 'Hello!',
          cache_control: { type: 'ephemeral' },
        },
      ],
    });
  });

  it('encodeMessages does NOT reuse rawMessage for different model', () => {
    // Create an assistant message from a different model
    const assistantMsg: AssistantMessage = {
      role: 'assistant',
      content: [{ type: 'text', text: 'Hello!' }],
      name: null,
      providerId: 'anthropic',
      modelId: 'anthropic/claude-sonnet-4-5', // Different model
      providerModelName: 'claude-sonnet-4-5',
      rawMessage: {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
      } as unknown as AssistantMessage['rawMessage'],
    };

    const messages = [user('Hi'), assistantMsg];
    // Request is for haiku, but message is from sonnet
    const { messages: encoded } = encodeMessages(
      messages,
      'anthropic/claude-haiku-4-5'
    );

    // Should encode from content, not raw message
    // Last message in multi-turn gets cache_control
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: 'Hello!',
          cache_control: { type: 'ephemeral' },
        },
      ],
    });
  });

  it('encodeMessages reuses rawMessage without structure validation', () => {
    // Create an assistant message with non-standard rawMessage
    const assistantMsg: AssistantMessage = {
      role: 'assistant',
      content: [{ type: 'text', text: 'Hello!' }],
      name: null,
      providerId: 'anthropic',
      modelId: 'anthropic/claude-haiku-4-5',
      providerModelName: 'claude-haiku-4-5',
      rawMessage: {
        // Even without proper 'role' and 'content' structure
        id: 'msg_123',
      } as unknown as AssistantMessage['rawMessage'],
    };

    // Add a third message so assistant is not last (last message gets cache_control
    // which would force re-encoding)
    const messages = [user('Hi'), assistantMsg, user('Bye')];
    const { messages: encoded } = encodeMessages(
      messages,
      'anthropic/claude-haiku-4-5'
    );

    // rawMessage IS reused (without structure validation) when provider/model match
    // and we're not adding cache control (assistant is not the last message)
    expect(encoded).toHaveLength(3);
    expect(encoded[1]).toEqual({ id: 'msg_123' });
  });
});

describe('automatic cache control', () => {
  describe('system message cache control', () => {
    it('adds cache_control to system message', () => {
      const messages = [
        { role: 'system', content: { type: 'text', text: 'You are helpful' } },
        user('Hello'),
      ] as const;

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        undefined,
        undefined,
        {}
      );

      // System should be an array with cache_control
      expect(Array.isArray(params.system)).toBe(true);
      expect(params.system).toEqual([
        {
          type: 'text',
          text: 'You are helpful',
          cache_control: { type: 'ephemeral' },
        },
      ]);
    });
  });

  describe('tool cache control', () => {
    it('adds cache_control to the last tool', () => {
      const messages = [user('Hello')];

      const tool1 = defineTool({
        name: 'get_weather',
        description: 'Get weather',
        tool: () => 'sunny',
        __schema: {
          type: 'object',
          properties: { location: { type: 'string' } },
          required: ['location'],
          additionalProperties: false,
        },
      });

      const tool2 = defineTool({
        name: 'get_time',
        description: 'Get time',
        tool: () => '12:00',
        __schema: {
          type: 'object',
          properties: { timezone: { type: 'string' } },
          required: ['timezone'],
          additionalProperties: false,
        },
      });

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        [tool1, tool2],
        undefined,
        {}
      );

      // First tool should NOT have cache_control
      expect(params.tools?.[0]).not.toHaveProperty('cache_control');

      // Last tool should have cache_control
      expect(params.tools?.[1]).toHaveProperty('cache_control', {
        type: 'ephemeral',
      });
    });

    it('adds cache_control to format tool when it is the only tool', () => {
      const messages = [user('Hello')];

      const format = defineFormat({
        mode: 'tool',
        __schema: {
          type: 'object',
          properties: { name: { type: 'string' } },
          required: ['name'],
          additionalProperties: false,
        },
      });

      const params = buildRequestParams(
        'anthropic/claude-haiku-4-5',
        messages,
        undefined,
        format,
        {}
      );

      // Format tool should have cache_control
      expect(params.tools?.[0]).toHaveProperty('cache_control', {
        type: 'ephemeral',
      });
    });
  });

  describe('multi-turn message cache control', () => {
    it('does NOT add cache_control for single-turn (user only) conversations', () => {
      const messages = [user('Hello')];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      // Single user message should be simplified to string (no cache_control)
      expect(encoded).toHaveLength(1);
      expect(encoded[0]).toEqual({ role: 'user', content: 'Hello' });
    });

    it('adds cache_control to last message in multi-turn conversations', () => {
      const assistantMsg: AssistantMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
        name: null,
        providerId: 'openai', // Different provider to force re-encoding
        modelId: 'openai/gpt-4o',
        providerModelName: 'gpt-4o',
        rawMessage: null,
      };

      const messages = [user('Hi'), assistantMsg, user('How are you?')];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      expect(encoded).toHaveLength(3);

      // First user message - no cache_control
      expect(encoded[0]).toEqual({ role: 'user', content: 'Hi' });

      // Assistant message - no cache_control
      expect(encoded[1]).toEqual({ role: 'assistant', content: 'Hello!' });

      // Last message should have cache_control (array format, not string)
      expect(encoded[2]).toEqual({
        role: 'user',
        content: [
          {
            type: 'text',
            text: 'How are you?',
            cache_control: { type: 'ephemeral' },
          },
        ],
      });
    });

    it('adds cache_control to multi-part content in multi-turn conversations', () => {
      // Create an image for multi-part content
      const pngMagicBytes = new Uint8Array([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
      ]);
      const image = Image.fromBytes(pngMagicBytes);

      const assistantMsg: AssistantMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'I see an image' }],
        name: null,
        providerId: 'openai', // Different provider to force re-encoding
        modelId: 'openai/gpt-4o',
        providerModelName: 'gpt-4o',
        rawMessage: null,
      };

      const messages = [
        user('Hi'),
        assistantMsg,
        user(['Look at this', image, 'What do you see?']),
      ];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      expect(encoded).toHaveLength(3);

      // Last message should be an array with cache_control on the last text block
      const lastMessage = encoded[2] as {
        role: string;
        content: Array<{ type: string; cache_control?: object }>;
      };
      expect(lastMessage.role).toBe('user');
      expect(Array.isArray(lastMessage.content)).toBe(true);
      expect(lastMessage.content).toHaveLength(3);

      // First text - no cache_control
      expect(lastMessage.content[0]).not.toHaveProperty('cache_control');
      // Image - no cache_control
      expect(lastMessage.content[1]).not.toHaveProperty('cache_control');
      // Last text - has cache_control
      expect(lastMessage.content[2]).toHaveProperty('cache_control', {
        type: 'ephemeral',
      });
    });

    it('does not reuse rawMessage when adding cache_control to multi-turn', () => {
      // Create an assistant message that matches the target model
      const assistantMsg: AssistantMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
        name: null,
        providerId: 'anthropic',
        modelId: 'anthropic/claude-haiku-4-5',
        providerModelName: 'claude-haiku-4-5',
        rawMessage: {
          role: 'assistant',
          content: [{ type: 'text', text: 'Hello!' }],
        } as unknown as AssistantMessage['rawMessage'],
      };

      // Last message is user, so assistant message should not need cache_control
      // and can reuse rawMessage
      const messages = [user('Hi'), assistantMsg, user('Bye')];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      expect(encoded).toHaveLength(3);

      // Assistant message should be reused from rawMessage
      expect(encoded[1]).toHaveProperty('content');
      expect((encoded[1] as { content: unknown[] }).content[0]).toHaveProperty(
        'text',
        'Hello!'
      );
    });

    it('skips empty text when finding cacheable content in multi-turn', () => {
      const assistantMsg: AssistantMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
        name: null,
        providerId: 'openai', // Different provider to force re-encoding
        modelId: 'openai/gpt-4o',
        providerModelName: 'gpt-4o',
        rawMessage: null,
      };

      // Last message has text followed by empty text - cache_control should
      // be added to the non-empty text, skipping the empty text
      const messages = [
        user('Hi'),
        assistantMsg,
        user(['What is this?', '']), // Non-empty text, then empty text
      ];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      expect(encoded).toHaveLength(3);

      // Last message should have cache_control on first (non-empty) text
      const lastMessage = encoded[2] as {
        role: string;
        content: Array<{ type: string; text: string; cache_control?: object }>;
      };
      expect(lastMessage.role).toBe('user');
      expect(Array.isArray(lastMessage.content)).toBe(true);

      // The first text block should have cache_control (empty text was skipped)
      expect(lastMessage.content[0]?.cache_control).toEqual({
        type: 'ephemeral',
      });
    });

    it('adds cache_control to image when it is the last cacheable content', () => {
      // PNG magic bytes
      const pngMagicBytes = new Uint8Array([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
      ]);
      const image = Image.fromBytes(pngMagicBytes);

      const assistantMsg: AssistantMessage = {
        role: 'assistant',
        content: [{ type: 'text', text: 'Hello!' }],
        name: null,
        providerId: 'openai', // Different provider to force re-encoding
        modelId: 'openai/gpt-4o',
        providerModelName: 'gpt-4o',
        rawMessage: null,
      };

      // Last message ends with an image - cache_control should be on the image
      const messages = [user('Hi'), assistantMsg, user([image])];

      const { messages: encoded } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      expect(encoded).toHaveLength(3);

      // Last message should have cache_control on the image
      const lastMessage = encoded[2] as {
        role: string;
        content: Array<{ type: string; cache_control?: object }>;
      };
      expect(lastMessage.role).toBe('user');
      expect(Array.isArray(lastMessage.content)).toBe(true);
      expect(lastMessage.content[0]?.type).toBe('image');
      expect(lastMessage.content[0]?.cache_control).toEqual({
        type: 'ephemeral',
      });
    });

    it('filters out system messages when encoding', () => {
      const messages = [
        {
          role: 'system' as const,
          content: { type: 'text' as const, text: 'Be helpful' },
        },
        user('Hi'),
      ];

      const { messages: encoded, system } = encodeMessages(
        messages,
        'anthropic/claude-haiku-4-5'
      );

      // System message should be extracted, not in encoded messages
      expect(system).toBe('Be helpful');
      expect(encoded).toHaveLength(1);
      expect(encoded[0]).toEqual({ role: 'user', content: 'Hi' });
    });
  });
});
