/**
 * Finish reason indicating why the model stopped generating.
 */

/**
 * Possible reasons why generation stopped.
 */
export const FinishReason = {
  /** Model ran out of tokens. */
  MAX_TOKENS: 'max_tokens',
  /** Model refused to generate. */
  REFUSAL: 'refusal',
  /** Context length exceeded. */
  CONTEXT_LENGTH_EXCEEDED: 'context_length_exceeded',
} as const;

/**
 * Type representing a finish reason value.
 */
export type FinishReason = (typeof FinishReason)[keyof typeof FinishReason];
