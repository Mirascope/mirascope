/**
 * HTTP client for the Mirascope registry.
 */

interface RegistryItem {
  name: string;
  type: string;
  files: Array<{
    path: string;
    target: string;
    content: string;
  }>;
  dependencies: {
    pip: string[];
    npm: string[];
  };
}

interface RegistryIndex {
  name: string;
  version: string;
  homepage: string;
  items: Array<{
    name: string;
    type: string;
    path: string;
    description?: string;
  }>;
}

export class RegistryClient {
  private baseUrl: string;

  constructor(baseUrl: string = "https://mirascope.com/registry") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async fetchIndex(): Promise<RegistryIndex | null> {
    const url = `${this.baseUrl}/r/index.json`;
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as RegistryIndex;
  }

  async fetchItem(
    name: string,
    language: string = "typescript",
  ): Promise<RegistryItem | null> {
    // Handle namespaced items (e.g., @mirascope/calculator)
    let itemName: string = name;
    if (name.startsWith("@")) {
      const parts = name.split("/");
      const lastPart = parts[parts.length - 1];
      if (parts.length >= 2 && lastPart) {
        itemName = lastPart;
      }
    }

    const url = `${this.baseUrl}/r/${itemName}.${language}.json`;
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as RegistryItem;
  }
}
