/**
 * @fileoverview The AsyncCall module for generating responses asynchronously using LLMs.
 */

import type { AsyncPrompt } from "../prompts";
import type { Response } from "../responses";
import { BaseCall } from "./base-call";

/**
 * A class for generating responses using LLMs asynchronously.
 */
export class AsyncCall<P extends any[] = any[]> extends BaseCall<P, AsyncPrompt<P>> {
  // Overloads for spread parameters
  call(...args: P): Promise<Response>;
  
  // Overload for single params object
  call(params: P extends [infer T] ? T : never): Promise<Response>;
  
  /**
   * Generates a response using the LLM asynchronously.
   * Accepts either spread parameters or a single params object.
   */
  async call(...args: any[]): Promise<Response> {
    throw new Error("Not implemented");
  }

  /**
   * Generates an asynchronous response using the LLM.
   * Alias for the call method.
   */
  async callAsync(...args: P): Promise<Response> {
    return await this.call(...args);
  }
}
