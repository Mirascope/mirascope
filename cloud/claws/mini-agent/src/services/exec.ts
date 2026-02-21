/**
 * Shell execution service as Effect Context.Tag.
 */
import { Context, Effect } from "effect";

import { ExecError } from "../errors.js";

export interface ExecResult {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
}

export interface ExecOptions {
  readonly sudo?: boolean;
  readonly sudoUser?: string;
  readonly timeout?: number;
}

export type ExecFn = (
  command: string,
  args?: string[],
  options?: ExecOptions,
) => Promise<ExecResult>;

export class Exec extends Context.Tag("Exec")<
  Exec,
  {
    readonly run: (
      command: string,
      args?: string[],
      options?: ExecOptions,
    ) => Effect.Effect<ExecResult, ExecError>;
    readonly runUnsafe: (
      command: string,
      args?: string[],
      options?: ExecOptions,
    ) => Effect.Effect<ExecResult, ExecError>;
  }
>() {}

/**
 * Create the live Exec service using Bun's shell.
 */
export const ExecLive = Effect.gen(function* () {
  const run = (
    command: string,
    args: string[] = [],
    options: ExecOptions = {},
  ): Effect.Effect<ExecResult, ExecError> =>
    Effect.tryPromise({
      try: async () => {
        let cmd = command;
        let cmdArgs = args;

        if (options.sudo) {
          cmdArgs = [cmd, ...cmdArgs];
          cmd = "sudo";
        } else if (options.sudoUser) {
          cmdArgs = ["-u", options.sudoUser, cmd, ...cmdArgs];
          cmd = "sudo";
        }

        const proc = Bun.spawn([cmd, ...cmdArgs], {
          stdout: "pipe",
          stderr: "pipe",
        });

        const [stdout, stderr] = await Promise.all([
          new Response(proc.stdout).text(),
          new Response(proc.stderr).text(),
        ]);

        const exitCode = await proc.exited;

        return { exitCode, stdout, stderr };
      },
      catch: (error) =>
        new ExecError({
          message: `Failed to execute: ${command} ${args.join(" ")}`,
          command,
          exitCode: -1,
          stderr: String(error),
        }),
    });

  const runUnsafe = (
    command: string,
    args: string[] = [],
    options: ExecOptions = {},
  ): Effect.Effect<ExecResult, ExecError> =>
    Effect.flatMap(run(command, args, options), (result) =>
      result.exitCode !== 0
        ? Effect.fail(
            new ExecError({
              message: `Command failed: ${command} ${args.join(" ")}`,
              command,
              exitCode: result.exitCode,
              stderr: result.stderr,
            }),
          )
        : Effect.succeed(result),
    );

  return { run, runUnsafe };
});
