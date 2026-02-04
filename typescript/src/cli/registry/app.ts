/**
 * Registry CLI - Manage registry items.
 */

import { defineCommand } from "citty";

import { addCommand } from "@/cli/registry/commands/add";
import { initCommand } from "@/cli/registry/commands/init";
import { listCommand } from "@/cli/registry/commands/list";

const DEFAULT_REGISTRY = "https://mirascope.com/registry";

export const app = defineCommand({
  meta: {
    name: "registry",
    description: "Manage registry items",
  },
  subCommands: {
    add: defineCommand({
      meta: {
        name: "add",
        description: "Add a registry item to your project",
      },
      args: {
        items: {
          type: "positional",
          description: "Name(s) of the registry item(s) to add",
          required: true,
        },
        path: {
          type: "string",
          alias: "p",
          description: "Custom path to install the item(s)",
        },
        overwrite: {
          type: "boolean",
          alias: "o",
          description: "Overwrite existing files",
          default: false,
        },
        registry: {
          type: "string",
          alias: "r",
          description: "Registry URL to fetch items from",
          default: DEFAULT_REGISTRY,
        },
      },
      async run({ args }) {
        const rawItems = args.items;
        const items: string[] = Array.isArray(rawItems) ? rawItems : [rawItems];
        await addCommand(items, args.path, args.overwrite, args.registry);
      },
    }),

    list: defineCommand({
      meta: {
        name: "list",
        description: "List available registry items",
      },
      args: {
        type: {
          type: "string",
          alias: "t",
          description: "Filter by item type (tool, agent, prompt, integration)",
        },
        registry: {
          type: "string",
          alias: "r",
          description: "Registry URL to list items from",
          default: DEFAULT_REGISTRY,
        },
      },
      async run({ args }) {
        await listCommand(args.type, args.registry);
      },
    }),

    init: defineCommand({
      meta: {
        name: "init",
        description: "Initialize Mirascope configuration in your project",
      },
      async run() {
        await initCommand();
      },
    }),
  },
});
