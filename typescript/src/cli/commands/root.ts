/**
 * @fileoverview Root CLI command tree for `mirascope`.
 */

import { Command } from "@effect/cli";

import { setKeyCommand } from "./auth/set-key.js";
import { createCommand } from "./claw/create.js";
import { deleteCommand } from "./claw/delete.js";
import { listCommand } from "./claw/list.js";
import { statusCommand } from "./claw/status.js";

// ---------------------------------------------------------------------------
// Auth subcommands
// ---------------------------------------------------------------------------

const authCommand = Command.make("auth").pipe(
  Command.withSubcommands([setKeyCommand]),
);

// ---------------------------------------------------------------------------
// Claw subcommands
// ---------------------------------------------------------------------------

const clawCommand = Command.make("claw").pipe(
  Command.withSubcommands([
    listCommand,
    createCommand,
    statusCommand,
    deleteCommand,
  ]),
);

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------

export const rootCommand = Command.make("mirascope").pipe(
  Command.withSubcommands([authCommand, clawCommand]),
);
