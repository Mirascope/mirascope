/**
 * Configuration management for the Mirascope CLI.
 */

import { join } from "path";

import type { MirascopeConfig } from "@/cli/registry/types";

export async function loadConfig(): Promise<MirascopeConfig | null> {
  const configPath = join(process.cwd(), "mirascope.json");

  // eslint-disable-next-line no-undef
  const file = Bun.file(configPath);
  if (!(await file.exists())) {
    return null;
  }

  try {
    return (await file.json()) as MirascopeConfig;
  } catch {
    return null;
  }
}
