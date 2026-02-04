/**
 * List command - List available registry items.
 */

import type { RegistryIndex, RegistryIndexItem } from "@/cli/registry/types";

import { RegistryClient } from "@/cli/registry/client";

interface ListOptions {
  itemType?: string;
  registryUrl: string;
}

export async function runList(options: ListOptions): Promise<number> {
  const { itemType, registryUrl } = options;

  const client = new RegistryClient(registryUrl);

  let index: RegistryIndex | null;
  try {
    index = await client.fetchIndex();
  } catch (e) {
    console.error(`Error: Failed to fetch registry index: ${String(e)}`);
    return 1;
  }

  if (!index) {
    console.error("Error: Could not fetch registry index.");
    return 1;
  }

  let items = index.items ?? [];

  // Filter by type if specified
  if (itemType) {
    items = items.filter((i) => i.type === itemType);
  }

  if (items.length === 0) {
    if (itemType) {
      console.log(`No items found with type '${itemType}'.`);
    } else {
      console.log("No items found in registry.");
    }
    return 0;
  }

  // Group by type
  const byType: Record<string, RegistryIndexItem[]> = {};
  for (const item of items) {
    const t = item.type ?? "other";
    if (!byType[t]) {
      byType[t] = [];
    }
    byType[t].push(item);
  }

  console.log(`Available items from ${registryUrl}:\n`);

  for (const [typeName, typeItems] of Object.entries(byType).sort()) {
    console.log(`${typeName.charAt(0).toUpperCase() + typeName.slice(1)}s:`);
    for (const item of typeItems) {
      const name = item.name ?? "unknown";
      const desc = item.description ?? "";
      console.log(`  ${name.padEnd(20)} ${desc}`);
    }
    console.log();
  }

  console.log("Use `mirascope add <name>` to install.");
  return 0;
}
