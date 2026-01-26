/**
 * Unit tests for Beta Anthropic decoding utilities.
 *
 * Tests beta-specific features like refusal stop reason and thinking blocks.
 */

import { describe, it, expect } from 'vitest';
import type { BetaMessage } from '@anthropic-ai/sdk/resources/beta/messages/messages';
import { betaDecodeResponse } from './beta-decode';
import { FinishReason } from '@/llm/responses/finish-reason';

/**
 * Create a mock BetaMessage for testing.
 */
function createMockBetaMessage(
  overrides: Partial<BetaMessage> = {}
): BetaMessage {
  return {
    id: 'msg_beta_123',
    type: 'message',
    role: 'assistant',
    content: [{ type: 'text', text: 'Hello!', citations: null }],
    model: 'claude-haiku-4-5',
    stop_reason: 'end_turn',
    stop_sequence: null,
    usage: {
      input_tokens: 10,
      output_tokens: 5,
      cache_read_input_tokens: 0,
      cache_creation_input_tokens: 0,
      cache_creation: null,
      server_tool_use: null,
      service_tier: 'standard',
    },
    container: null,
    ...overrides,
  } as BetaMessage;
}

describe('betaDecodeResponse', () => {
  describe('stop reason handling', () => {
    it('maps refusal stop reason to REFUSAL', () => {
      const response = createMockBetaMessage({ stop_reason: 'refusal' });

      const { finishReason } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(finishReason).toBe(FinishReason.REFUSAL);
    });

    it('maps max_tokens stop reason to MAX_TOKENS', () => {
      const response = createMockBetaMessage({ stop_reason: 'max_tokens' });

      const { finishReason } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(finishReason).toBe(FinishReason.MAX_TOKENS);
    });

    it('maps end_turn to null (normal completion)', () => {
      const response = createMockBetaMessage({ stop_reason: 'end_turn' });

      const { finishReason } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(finishReason).toBeNull();
    });

    it('maps pause_turn to null', () => {
      const response = createMockBetaMessage({ stop_reason: 'pause_turn' });

      const { finishReason } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(finishReason).toBeNull();
    });
  });

  describe('content handling', () => {
    it('decodes text content', () => {
      const response = createMockBetaMessage({
        content: [{ type: 'text', text: 'Test response', citations: null }],
      });

      const { assistantMessage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(assistantMessage.content).toEqual([
        { type: 'text', text: 'Test response' },
      ]);
    });

    it('skips thinking blocks', () => {
      const response = createMockBetaMessage({
        content: [
          {
            type: 'thinking',
            thinking: 'Internal reasoning...',
            signature: 'sig',
          },
          { type: 'text', text: 'Visible response', citations: null },
        ],
      } as Partial<BetaMessage>);

      const { assistantMessage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      // Only text content should be included
      expect(assistantMessage.content).toEqual([
        { type: 'text', text: 'Visible response' },
      ]);
    });

    it('skips redacted_thinking blocks', () => {
      const response = createMockBetaMessage({
        content: [
          { type: 'redacted_thinking', data: 'redacted' },
          {
            type: 'text',
            text: 'Response after redacted thinking',
            citations: null,
          },
        ],
      } as Partial<BetaMessage>);

      const { assistantMessage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(assistantMessage.content).toEqual([
        { type: 'text', text: 'Response after redacted thinking' },
      ]);
    });
  });

  describe('usage handling', () => {
    it('decodes usage with cache tokens', () => {
      const response = createMockBetaMessage({
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_read_input_tokens: 20,
          cache_creation_input_tokens: 10,
          cache_creation: null,
          server_tool_use: null,
          service_tier: 'standard',
        },
      });

      const { usage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(usage).not.toBeNull();
      expect(usage!.inputTokens).toBe(100);
      expect(usage!.outputTokens).toBe(50);
      expect(usage!.cacheReadTokens).toBe(20);
      expect(usage!.cacheWriteTokens).toBe(10);
    });

    it('handles null cache tokens', () => {
      const response = createMockBetaMessage({
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_read_input_tokens: null,
          cache_creation_input_tokens: null,
          cache_creation: null,
          server_tool_use: null,
          service_tier: null,
        },
      });

      const { usage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      expect(usage).not.toBeNull();
      expect(usage!.cacheReadTokens).toBe(0);
      expect(usage!.cacheWriteTokens).toBe(0);
    });
  });

  describe('metadata', () => {
    it('sets providerId to anthropic (not anthropic-beta)', () => {
      const response = createMockBetaMessage();

      const { assistantMessage } = betaDecodeResponse(
        response,
        'anthropic/claude-haiku-4-5'
      );

      // This matches Python SDK behavior
      expect(assistantMessage.providerId).toBe('anthropic');
    });

    it('preserves modelId', () => {
      const response = createMockBetaMessage();

      const { assistantMessage } = betaDecodeResponse(
        response,
        'anthropic-beta/claude-sonnet-4-0'
      );

      expect(assistantMessage.modelId).toBe('anthropic-beta/claude-sonnet-4-0');
    });
  });
});
