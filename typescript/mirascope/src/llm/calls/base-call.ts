/**
 * @fileoverview The `BaseCall` class for LLM calls.
 */

import type { LLM } from "../models";
import type { AsyncPrompt, Prompt } from "../prompts";

/**
 * A base class for generating responses using LLMs.
 */
export abstract class BaseCall<
  P extends any[] = any[],
  PromptT extends Prompt<P> | AsyncPrompt<P> = Prompt<P> | AsyncPrompt<P>
> {
  /**
   * The LLM model used for generating responses.
   */
  model: LLM;

  /**
   * The Prompt function that generates the Prompt.
   */
  fn: PromptT;

  constructor(
    model: LLM,
    fn: PromptT
  ) {
    this.model = model;
    this.fn = fn;
  }
}
