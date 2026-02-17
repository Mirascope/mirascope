/**
 * Test helpers — mock exec function and utilities.
 */
import type { ExecFn, ExecResult } from "../src/lib/exec.js";

export interface MockExecCall {
  command: string;
  args: string[];
  options: unknown;
}

/**
 * Create a mock exec function that records calls and returns preconfigured responses.
 */
export function createMockExec(
  responses: Map<string, ExecResult> = new Map(),
): {
  exec: ExecFn;
  calls: MockExecCall[];
} {
  const calls: MockExecCall[] = [];

  const exec: ExecFn = async (command, args = [], options = {}) => {
    calls.push({ command, args, options });

    // Build a key from the command for lookup
    const fullCmd = [command, ...args].join(" ");

    // Check exact match first
    for (const [pattern, result] of responses) {
      if (fullCmd.includes(pattern)) {
        return result;
      }
    }

    // Default: success
    return { exitCode: 0, stdout: "", stderr: "" };
  };

  return { exec, calls };
}

export function successResult(stdout = ""): ExecResult {
  return { exitCode: 0, stdout, stderr: "" };
}

export function failResult(
  stderr = "command failed",
  exitCode = 1,
): ExecResult {
  return { exitCode, stdout: "", stderr };
}
