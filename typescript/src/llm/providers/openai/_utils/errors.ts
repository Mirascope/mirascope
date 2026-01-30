/**
 * OpenAI error mapping from SDK exceptions to Mirascope error types.
 */

import OpenAI from "openai";

import type { ProviderErrorMap } from "@/llm/providers/base";

import {
  APIError,
  AuthenticationError,
  BadRequestError,
  ConnectionError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from "@/llm/exceptions";

/**
 * Error mapping from OpenAI SDK exceptions to Mirascope error types.
 * Note: More specific error classes must come before their parent classes
 * since the error map is checked with instanceof in order.
 */
export const OPENAI_ERROR_MAP: ProviderErrorMap = [
  [OpenAI.AuthenticationError, AuthenticationError],
  [OpenAI.PermissionDeniedError, PermissionError],
  [OpenAI.NotFoundError, NotFoundError],
  [OpenAI.BadRequestError, BadRequestError],
  [OpenAI.UnprocessableEntityError, BadRequestError],
  [OpenAI.ConflictError, BadRequestError],
  [OpenAI.RateLimitError, RateLimitError],
  [OpenAI.InternalServerError, ServerError],
  [OpenAI.APIConnectionTimeoutError, TimeoutError],
  [OpenAI.APIConnectionError, ConnectionError],
  [OpenAI.APIError, APIError],
];
