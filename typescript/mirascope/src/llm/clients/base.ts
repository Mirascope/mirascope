/**
 * @fileoverview Base abstract interface for provider clients.
 */

import type { Response } from '../responses';
import type { REGISTERED_LLMS } from './register';

/**
 * Common parameters shared across LLM providers.
 *
 * Note: Each provider may handle these parameters differently or not support them at all.
 * Please check provider-specific documentation for parameter support and behavior.
 */
export interface BaseParams {
  /**
   * Controls randomness in the output (0.0 to 1.0).
   */
  temperature?: number;

  /**
   * Maximum number of tokens to generate.
   */
  maxTokens?: number;

  /**
   * Nucleus sampling parameter (0.0 to 1.0).
   */
  topP?: number;

  /**
   * Penalizes frequent tokens (-2.0 to 2.0).
   */
  frequencyPenalty?: number;

  /**
   * Penalizes tokens based on presence (-2.0 to 2.0).
   */
  presencePenalty?: number;

  /**
   * Random seed for reproducibility.
   */
  seed?: number;

  /**
   * Stop sequence(s) to end generation.
   */
  stop?: string | string[];
}

/**
 * Base abstract client for provider-specific implementations.
 *
 * This class defines explicit methods for each type of call, eliminating
 * the need for complex overloads in provider implementations.
 */
export abstract class BaseClient<
  MessageT = any,
  ParamsT extends BaseParams = BaseParams,
  LLMT extends REGISTERED_LLMS = REGISTERED_LLMS,
> {
  /**
   * Generate a standard response.
   */
  abstract call(args: {
    model: LLMT;
    messages: MessageT[];
    params?: ParamsT | null;
  }): Response;

  /**
   * Generate a standard response asynchronously.
   */
  abstract callAsync(args: {
    model: LLMT;
    messages: MessageT[];
    params?: ParamsT | null;
  }): Promise<Response>;
}
