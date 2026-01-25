/**
 * Unit tests for Google provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping that can't be tested via successful API calls.
 */

import { describe, it, expect } from 'vitest';
import {
  AuthenticationError,
  PermissionError,
  NotFoundError,
  RateLimitError,
  BadRequestError,
  ServerError,
  APIError,
} from '@/llm/exceptions';
import { mapGoogleErrorByStatus } from './_utils';

describe('mapGoogleErrorByStatus', () => {
  it('maps 401 to AuthenticationError', () => {
    expect(mapGoogleErrorByStatus(401)).toBe(AuthenticationError);
  });

  it('maps 403 to PermissionError', () => {
    expect(mapGoogleErrorByStatus(403)).toBe(PermissionError);
  });

  it('maps 404 to NotFoundError', () => {
    expect(mapGoogleErrorByStatus(404)).toBe(NotFoundError);
  });

  it('maps 429 to RateLimitError', () => {
    expect(mapGoogleErrorByStatus(429)).toBe(RateLimitError);
  });

  it('maps 400 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(400)).toBe(BadRequestError);
  });

  it('maps 422 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(422)).toBe(BadRequestError);
  });

  it('maps 5xx to ServerError', () => {
    expect(mapGoogleErrorByStatus(500)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(502)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(503)).toBe(ServerError);
  });

  it('maps unknown status codes to APIError', () => {
    expect(mapGoogleErrorByStatus(418)).toBe(APIError);
    expect(mapGoogleErrorByStatus(499)).toBe(APIError);
  });
});
