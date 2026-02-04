/**
 * Init command - Initialize Mirascope configuration.
 */

import { join } from "path";

interface MirascopeConfig {
  $schema: string;
  language: string;
  registry: string;
  paths: {
    tools: string;
    agents: string;
    prompts: string;
    integrations: string;
  };
}

export async function runInit(): Promise<number> {
  const configPath = join(process.cwd(), "mirascope.json");

  // eslint-disable-next-line no-undef
  const file = Bun.file(configPath);
  if (await file.exists()) {
    console.log(`Configuration already exists at ${configPath}`);
    return 0;
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
      "\nYou can now use `mirascope add <item>` to add registry items.",
    );
  } catch (e) {
    console.error(`Error: Failed to create config file: ${String(e)}`);
    return 1;
  }

  return 0;
}
