#!/usr/bin/env bun
/**
 * Mirascope CLI - Command-line interface for the Mirascope registry.
 */

import { parseArgs } from "util";

import { runAdd } from "./commands/add";
import { runInit } from "./commands/init";
import { runList } from "./commands/list";

const VERSION = "0.1.0";
const DEFAULT_REGISTRY = "https://mirascope.com/registry";

function printHelp(): void {
  console.log(`
Mirascope CLI - Install registry items into your project

Usage: mirascope <command> [options]

Commands:
  add <items...>    Add registry item(s) to your project
  list              List available registry items
  init              Initialize Mirascope configuration in your project

Options:
  -h, --help        Show this help message
  -v, --version     Show version number

Examples:
  mirascope add calculator
  mirascope add calculator web-search
  mirascope list --type tool
  mirascope init
`);
}

async function main(): Promise<number> {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
    printHelp();
    return 0;
  }

  if (args[0] === "-v" || args[0] === "--version") {
    console.log(`mirascope ${VERSION}`);
    return 0;
  }

  const command = args[0];
  const commandArgs = args.slice(1);

  switch (command) {
    case "add": {
      const { values, positionals } = parseArgs({
        args: commandArgs,
        options: {
          path: { type: "string", short: "p" },
          overwrite: { type: "boolean", short: "o", default: false },
          registry: { type: "string", short: "r", default: DEFAULT_REGISTRY },
        },
        allowPositionals: true,
      });

      if (positionals.length === 0) {
        console.error(
          "Error: No items specified. Usage: mirascope add <items...>",
        );
        return 1;
      }

      return await runAdd({
        items: positionals,
        path: values.path,
        overwrite: values.overwrite ?? false,
        registryUrl: values.registry ?? DEFAULT_REGISTRY,
      });
    }

    case "list": {
      const { values } = parseArgs({
        args: commandArgs,
        options: {
          type: { type: "string", short: "t" },
          registry: { type: "string", short: "r", default: DEFAULT_REGISTRY },
        },
        allowPositionals: false,
      });

      return await runList({
        itemType: values.type,
        registryUrl: values.registry ?? DEFAULT_REGISTRY,
      });
    }

    case "init": {
      return await runInit();
    }

    default:
      console.error(`Error: Unknown command '${command}'`);
      printHelp();
      return 1;
  }
}

main()
  .then((code) => process.exit(code))
  .catch((err) => {
    console.error("Error:", err);
    process.exit(1);
  });
