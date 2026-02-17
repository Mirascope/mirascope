/**
 * Shell execution service — Effect-based wrapper around child_process.execFile.
 */
import { execFile as execFileCb } from "node:child_process";
import { promisify } from "node:util";

import { Context, Effect, Layer } from "effect";

const execFileAsync = promisify(execFileCb);

export interface ExecResult {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
}

export interface ExecOptions {
  readonly timeout?: number;
  readonly cwd?: string;
  readonly env?: Record<string, string>;
  readonly sudo?: boolean;
  readonly sudoUser?: string;
}

export interface ExecService {
  readonly run: (
    command: string,
    args?: string[],
    options?: ExecOptions,
  ) => Effect.Effect<ExecResult>;
}

export class Exec extends Context.Tag("MiniAgent/Exec")<
  Exec,
  ExecService
>() {}

export const ExecLive = Layer.succeed(Exec, {
  run: (command, args = [], options = {}) =>
    Effect.promise(async () => {
      const timeout = options.timeout ?? 30_000;

      let finalCommand = command;
      let finalArgs = args;

      if (options.sudoUser) {
        finalArgs = ["-u", options.sudoUser, command, ...args];
        finalCommand = "sudo";
      } else if (options.sudo) {
        finalArgs = [command, ...args];
        finalCommand = "sudo";
      }

      const logCmd = [finalCommand, ...finalArgs].join(" ");
      console.log(`[exec] ${logCmd}`);

      try {
        const { stdout, stderr } = await execFileAsync(
          finalCommand,
          finalArgs,
          {
            timeout,
            cwd: options.cwd,
            env: options.env
              ? { ...process.env, ...options.env }
              : undefined,
            maxBuffer: 10 * 1024 * 1024,
          },
        );

        if (stderr) {
          console.log(`[exec] stderr: ${stderr.slice(0, 500)}`);
        }
        return { exitCode: 0, stdout, stderr };
      } catch (error: unknown) {
        const err = error as Record<string, unknown>;
        const result: ExecResult = {
          exitCode:
            err.code === "ERR_CHILD_PROCESS_TIMEOUT"
              ? 124
              : ((err.status ?? err.code ?? 1) as number),
          stdout: (err.stdout as string) ?? "",
          stderr: (err.stderr as string) ?? (err.message as string) ?? "",
        };
        console.error(
          `[exec] FAILED (exit ${result.exitCode}): ${logCmd}`,
        );
        console.error(`[exec] stderr: ${result.stderr.slice(0, 500)}`);
        return result;
      }
    }),
});
