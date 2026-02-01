import type { Jsonable } from "@/llm/types/jsonable";

/**
 * Tool output content representing the result of a tool call.
 *
 * Contains the result of executing a tool, or an error if the tool failed.
 * The generic type T allows for typed results when the tool output type is known.
 */
export type ToolOutput<T extends Jsonable = Jsonable> = {
  readonly type: "tool_output";

  /** The ID of the tool call that this output is for. */
  readonly id: string;

  /** The name of the tool that created this output. */
  readonly name: string;

  /**
   * The result of calling the tool.
   *
   * If the tool executed successfully, this will be the tool output.
   * If the tool errored, this will be the error message, as a string.
   */
  readonly result: T | string;

  /** The error from calling the tool, if any. */
  readonly error: Error | null;
};

/**
 * Factory methods for creating ToolOutput instances.
 */
export const ToolOutput = {
  /**
   * Create a ToolOutput with explicit parameters.
   */
  create: <T extends Jsonable>(
    id: string,
    name: string,
    result: T | string,
    error: Error | null = null,
  ): ToolOutput<T> => ({
    type: "tool_output",
    id,
    name,
    result,
    error,
  }),

  /**
   * Create a successful ToolOutput.
   */
  success: <T extends Jsonable>(
    id: string,
    name: string,
    result: T,
  ): ToolOutput<T> => ({
    type: "tool_output",
    id,
    name,
    result,
    error: null,
  }),

  /**
   * Create a failed ToolOutput.
   */
  failure: (id: string, name: string, error: Error): ToolOutput => ({
    type: "tool_output",
    id,
    name,
    result: error.message,
    error,
  }),
};
