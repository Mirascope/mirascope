/**
 * @fileoverview The Call module for generating responses using LLMs.
 */

import type { Prompt } from "../prompts";
import type { Response } from "../responses";
import { BaseCall } from "./base-call";

// TODO: figure out named call parameters

/**
 * A class for generating responses using LLMs.
 */
export class Call<P extends any[] = any[]> extends BaseCall<P, Prompt<P>> {
  /**
   * Generates a response using the LLM.
   */
  call(...args: P): Response {
    throw new Error("Not implemented");
  }

  /**
   * Generates an asynchronous response using the LLM.
   */
  async callAsync(...args: P): Promise<Response> {
    throw new Error("Not implemented");
  }
}
