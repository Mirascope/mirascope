/**
 * Init command - Initialize Mirascope configuration.
 */

import { join } from "path";

import type { MirascopeConfig } from "@/cli/registry/types";

export async function initCommand(): Promise<void> {
  const configPath = join(process.cwd(), "mirascope.json");

  // eslint-disable-next-line no-undef
  const file = Bun.file(configPath);
  if (await file.exists()) {
    console.log(`Configuration already exists at ${configPath}`);
    return;
  }

  const config: MirascopeConfig = {
    $schema: "https://mirascope.com/registry/schema/config.json",
    language: "typescript",
    registry: "https://mirascope.com/registry",
    paths: {
      tools: "ai/tools",
      agents: "ai/agents",
      prompts: "ai/prompts",
      integrations: "ai/integrations",
    },
  };

  try {
    // eslint-disable-next-line no-undef
    await Bun.write(configPath, JSON.stringify(config, null, 2) + "\n");
    console.log(`Created ${configPath}`);
    console.log(
      "\nYou can now use `mirascope registry add <item>` to add registry items.",
    );
  } catch (e) {
    console.error(`Error: Failed to create config file: ${String(e)}`);
    process.exit(1);
    return;
  }
}
