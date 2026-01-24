import { describe, expect, it } from 'vitest';
import {
  MirascopeError,
  ProviderError,
  APIError,
  AuthenticationError,
  PermissionError,
  BadRequestError,
  NotFoundError,
  RateLimitError,
  ServerError,
  ConnectionError,
  TimeoutError,
  ResponseValidationError,
  ToolError,
  ToolExecutionError,
  ToolNotFoundError,
  ParseError,
  FeatureNotSupportedError,
  NoRegisteredProviderError,
  MissingAPIKeyError,
} from '@/llm/exceptions';

describe('MirascopeError', () => {
  it('sets the error name to the class name', () => {
    const error = new MirascopeError('test message');

    expect(error.name).toBe('MirascopeError');
    expect(error.message).toBe('test message');
  });

  it('is an instance of Error', () => {
    const error = new MirascopeError('test');

    expect(error).toBeInstanceOf(Error);
  });
});

describe('ProviderError', () => {
  it('stores provider and original exception', () => {
    const original = new Error('original error');
    const error = new ProviderError('provider failed', 'openai', original);

    expect(error.provider).toBe('openai');
    expect(error.originalException).toBe(original);
    expect(error.cause).toBe(original);
  });

  it('handles null original exception', () => {
    const error = new ProviderError('provider failed', 'anthropic');

    expect(error.provider).toBe('anthropic');
    expect(error.originalException).toBeNull();
    expect(error.cause).toBeUndefined();
  });
});

describe('APIError', () => {
  it('stores status code', () => {
    const error = new APIError('api error', 'openai', 500);

    expect(error.statusCode).toBe(500);
    expect(error.provider).toBe('openai');
  });

  it('handles null status code', () => {
    const error = new APIError('api error', 'openai');

    expect(error.statusCode).toBeNull();
  });
});

describe('AuthenticationError', () => {
  it('defaults to status code 401', () => {
    const error = new AuthenticationError('invalid key', 'openai');

    expect(error.statusCode).toBe(401);
  });

  it('allows custom status code', () => {
    const error = new AuthenticationError('invalid key', 'openai', 403);

    expect(error.statusCode).toBe(403);
  });
});

describe('PermissionError', () => {
  it('defaults to status code 403', () => {
    const error = new PermissionError('access denied', 'anthropic');

    expect(error.statusCode).toBe(403);
  });
});

describe('BadRequestError', () => {
  it('defaults to status code 400', () => {
    const error = new BadRequestError('bad request', 'google');

    expect(error.statusCode).toBe(400);
  });

  it('allows 422 status code', () => {
    const error = new BadRequestError('validation error', 'google', 422);

    expect(error.statusCode).toBe(422);
  });
});

describe('NotFoundError', () => {
  it('defaults to status code 404', () => {
    const error = new NotFoundError('not found', 'openai');

    expect(error.statusCode).toBe(404);
  });
});

describe('RateLimitError', () => {
  it('defaults to status code 429', () => {
    const error = new RateLimitError('rate limited', 'anthropic');

    expect(error.statusCode).toBe(429);
  });
});

describe('ServerError', () => {
  it('defaults to status code 500', () => {
    const error = new ServerError('internal error', 'openai');

    expect(error.statusCode).toBe(500);
  });

  it('allows 503 status code', () => {
    const error = new ServerError('service unavailable', 'openai', 503);

    expect(error.statusCode).toBe(503);
  });
});

describe('ConnectionError', () => {
  it('extends ProviderError', () => {
    const error = new ConnectionError('network error', 'google');

    expect(error).toBeInstanceOf(ProviderError);
    expect(error.provider).toBe('google');
  });
});

describe('TimeoutError', () => {
  it('extends ProviderError', () => {
    const error = new TimeoutError('request timed out', 'anthropic');

    expect(error).toBeInstanceOf(ProviderError);
  });
});

describe('ResponseValidationError', () => {
  it('extends ProviderError', () => {
    const error = new ResponseValidationError('invalid response', 'openai');

    expect(error).toBeInstanceOf(ProviderError);
  });
});

describe('ToolError', () => {
  it('extends MirascopeError', () => {
    const error = new ToolError('tool error');

    expect(error).toBeInstanceOf(MirascopeError);
  });
});

describe('ToolExecutionError', () => {
  it('wraps an Error exception', () => {
    const original = new Error('execution failed');
    const error = new ToolExecutionError(original);

    expect(error.toolException).toBe(original);
    expect(error.message).toBe('execution failed');
    expect(error.cause).toBe(original);
  });

  it('creates Error from string for snapshot reconstruction', () => {
    const error = new ToolExecutionError('string error');

    expect(error.toolException).toBeInstanceOf(Error);
    expect(error.toolException.message).toBe('string error');
    expect(error.message).toBe('string error');
  });
});

describe('ToolNotFoundError', () => {
  it('stores tool name and generates message', () => {
    const error = new ToolNotFoundError('get_weather');

    expect(error.toolName).toBe('get_weather');
    expect(error.message).toBe(
      "Tool 'get_weather' not found in registered tools"
    );
  });
});

describe('ParseError', () => {
  it('stores original exception', () => {
    const original = new Error('parse failed');
    const error = new ParseError('could not parse', original);

    expect(error.originalException).toBe(original);
    expect(error.cause).toBe(original);
  });

  describe('retryMessage', () => {
    it('returns JSON-specific message for SyntaxError with JSON', () => {
      const original = new SyntaxError('Unexpected token in JSON');
      const error = new ParseError('parse failed', original);

      const message = error.retryMessage();

      expect(message).toContain('no valid JSON object was found');
      expect(message).toContain("opening '{'");
    });

    it('returns generic message for other errors', () => {
      const original = new Error('some other error');
      const error = new ParseError('parse failed', original);

      const message = error.retryMessage();

      expect(message).toContain('some other error');
      expect(message).toContain('matches the expected format');
    });
  });
});

describe('FeatureNotSupportedError', () => {
  it('generates message with provider only', () => {
    const error = new FeatureNotSupportedError('streaming', 'anthropic');

    expect(error.feature).toBe('streaming');
    expect(error.providerId).toBe('anthropic');
    expect(error.modelId).toBeNull();
    expect(error.message).toBe(
      "Feature 'streaming' is not supported by provider 'anthropic'"
    );
  });

  it('generates message with provider and model', () => {
    const error = new FeatureNotSupportedError(
      'thinking',
      'openai',
      'openai/gpt-4o'
    );

    expect(error.modelId).toBe('openai/gpt-4o');
    expect(error.message).toContain("for model 'openai/gpt-4o'");
  });

  it('uses custom message when provided', () => {
    const error = new FeatureNotSupportedError(
      'feature',
      'provider',
      null,
      'Custom error message'
    );

    expect(error.message).toBe('Custom error message');
  });
});

describe('NoRegisteredProviderError', () => {
  it('stores model ID and generates message', () => {
    const error = new NoRegisteredProviderError('custom/model');

    expect(error.modelId).toBe('custom/model');
    expect(error.message).toContain('No provider registered for model');
    expect(error.message).toContain('custom/model');
    expect(error.message).toContain('registerProvider()');
  });
});

describe('MissingAPIKeyError', () => {
  it('generates message without fallback', () => {
    const error = new MissingAPIKeyError('openai', 'OPENAI_API_KEY');

    expect(error.providerId).toBe('openai');
    expect(error.envVar).toBe('OPENAI_API_KEY');
    expect(error.message).toContain('No API key found for openai');
    expect(error.message).toContain('OPENAI_API_KEY');
    expect(error.message).not.toContain('MIRASCOPE_API_KEY');
  });

  it('generates message with fallback', () => {
    const error = new MissingAPIKeyError(
      'anthropic',
      'ANTHROPIC_API_KEY',
      true
    );

    expect(error.message).toContain('Either:');
    expect(error.message).toContain('ANTHROPIC_API_KEY');
    expect(error.message).toContain('MIRASCOPE_API_KEY');
    expect(error.message).toContain('mirascope.com/docs/router');
  });
});
