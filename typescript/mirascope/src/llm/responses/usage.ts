/**
 * @fileoverview The LLM's usage when generating a response.
 */

/**
 * The usage statistics for a request to an LLM.
 */
export type Usage = {
  /**
   * Number of tokens in the prompt (including messages, tools, etc).
   */
  inputTokens: number;

  /**
   * Number of tokens used that were previously cached (and thus cheaper).
   */
  cachedTokens: number;

  /**
   * Number of tokens in the generated output.
   *
   * TODO: figure out different types of output and how to handle that (e.g. audio)
   */
  outputTokens: number;

  /**
   * Total number of tokens used in the request (prompt + completion).
   */
  totalTokens: number;
};
