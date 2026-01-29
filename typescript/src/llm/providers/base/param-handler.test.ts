/**
 * Tests for ParamHandler utility.
 */

import { describe, it, expect, vi } from 'vitest';
import { ParamHandler } from '@/llm/providers/base/param-handler';
import { FeatureNotSupportedError } from '@/llm/exceptions';

describe('ParamHandler', () => {
  describe('with()', () => {
    it('executes callback and checks all params', () => {
      const result = ParamHandler.with(
        { maxTokens: 100 },
        'anthropic',
        'claude-sonnet-4',
        (p) => {
          return p.get('maxTokens');
        }
      );
      expect(result).toBe(100);
    });

    it('throws if unhandled params remain', () => {
      expect(() =>
        ParamHandler.with(
          { maxTokens: 100, temperature: 0.5 },
          'anthropic',
          'claude-sonnet-4',
          (p) => {
            p.get('maxTokens');
            // temperature not handled
          }
        )
      ).toThrow(FeatureNotSupportedError);
    });
  });

  describe('get()', () => {
    it('returns param value and marks as handled', () => {
      const handler = new ParamHandler(
        { temperature: 0.7 },
        'anthropic',
        'claude-sonnet-4'
      );
      expect(handler.get('temperature')).toBe(0.7);
      // Should not throw - param was handled
      handler.checkAllHandled();
    });

    it('returns undefined for missing params', () => {
      const handler = new ParamHandler({}, 'anthropic', 'claude-sonnet-4');
      expect(handler.get('temperature')).toBeUndefined();
    });
  });

  describe('getOrDefault()', () => {
    it('returns param value when set', () => {
      const handler = new ParamHandler(
        { maxTokens: 500 },
        'anthropic',
        'claude-sonnet-4'
      );
      expect(handler.getOrDefault('maxTokens', 1000)).toBe(500);
    });

    it('returns default when param not set', () => {
      const handler = new ParamHandler({}, 'anthropic', 'claude-sonnet-4');
      expect(handler.getOrDefault('maxTokens', 1000)).toBe(1000);
    });
  });

  describe('has()', () => {
    it('returns true when param is set', () => {
      const handler = new ParamHandler(
        { temperature: 0.5 },
        'anthropic',
        'claude-sonnet-4'
      );
      expect(handler.has('temperature')).toBe(true);
      handler.checkAllHandled();
    });

    it('returns false when param is not set', () => {
      const handler = new ParamHandler({}, 'anthropic', 'claude-sonnet-4');
      expect(handler.has('temperature')).toBe(false);
    });
  });

  describe('warnNotImplemented()', () => {
    it('logs warning when param is set', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler(
        { thinking: { level: 'high' } },
        'anthropic',
        'claude-sonnet-4'
      );

      handler.warnNotImplemented('thinking', 'thinking config');

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('thinking config is not yet implemented')
      );
      warnSpy.mockRestore();
    });

    it('does not log when param is not set', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler({}, 'anthropic', 'claude-sonnet-4');

      handler.warnNotImplemented('thinking', 'thinking config');

      expect(warnSpy).not.toHaveBeenCalled();
      warnSpy.mockRestore();
    });

    it('does not log when param is null', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler(
        { thinking: null },
        'anthropic',
        'claude-sonnet-4'
      );

      handler.warnNotImplemented('thinking', 'thinking config');

      expect(warnSpy).not.toHaveBeenCalled();
      warnSpy.mockRestore();
    });
  });

  describe('warnUnsupported()', () => {
    it('logs warning when param is set', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler(
        { seed: 42 },
        'anthropic',
        'claude-sonnet-4'
      );

      handler.warnUnsupported('seed', 'Anthropic does not support seed');

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Anthropic does not support seed')
      );
      warnSpy.mockRestore();
    });

    it('does not log when param is not set', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler({}, 'anthropic', 'claude-sonnet-4');

      handler.warnUnsupported('seed', 'Anthropic does not support seed');

      expect(warnSpy).not.toHaveBeenCalled();
      warnSpy.mockRestore();
    });

    it('uses default message when not provided', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const handler = new ParamHandler(
        { seed: 42 },
        'anthropic',
        'claude-sonnet-4'
      );

      handler.warnUnsupported('seed');

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "anthropic does not support the 'seed' parameter"
        )
      );
      warnSpy.mockRestore();
    });
  });

  describe('checkAllHandled()', () => {
    it('passes when all params are handled', () => {
      const handler = new ParamHandler(
        { maxTokens: 100, temperature: 0.5 },
        'anthropic',
        'claude-sonnet-4'
      );
      handler.get('maxTokens');
      handler.get('temperature');

      expect(() => handler.checkAllHandled()).not.toThrow();
    });

    it('throws for unhandled params', () => {
      const handler = new ParamHandler(
        { maxTokens: 100, unknownParam: 'value' } as Record<string, unknown>,
        'anthropic',
        'claude-sonnet-4'
      );
      handler.get('maxTokens');

      expect(() => handler.checkAllHandled()).toThrow(
        /Unknown parameter 'unknownParam'/
      );
    });
  });
});
