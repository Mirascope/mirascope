/**
 * DocRegistry - A singleton service for efficient document information management
 *
 * Canonical doc info, fast lookups, section/weight hierarchy.
 * Note: Cannot use import aliases in this file.
 */

import type { FullDocsSpec, DocInfo } from "./spec";

import { docsSpec } from "../../../../content/docs/_meta";
import { getDocsFromSpec } from "./spec";

/**
 * DocRegistry service - Singleton for efficient document information management
 */
class DocRegistry {
  private static instance: DocRegistry;

  // List of all docs from the spec
  private readonly allDocs: DocInfo[];

  // Path lookup map for efficient querying
  private readonly pathToDocInfo: Map<string, DocInfo>;

  private constructor() {
    // Initialize lookup
    this.pathToDocInfo = new Map();

    // Process the full docs spec to generate all DocInfo objects
    this.allDocs = getDocsFromSpec(docsSpec);

    // Build lookup map for efficient access
    this.buildLookupMaps();
  }

  /**
   * Get the singleton instance
   */
  public static getInstance(): DocRegistry {
    if (!DocRegistry.instance) {
      DocRegistry.instance = new DocRegistry();
    }
    return DocRegistry.instance;
  }

  /**
   * Builds efficient lookup map for content paths
   */
  private buildLookupMaps(): void {
    for (const docInfo of this.allDocs) {
      // Map content paths to DocInfo (for content loading)
      this.pathToDocInfo.set(docInfo.path, docInfo);
    }
  }

  /**
   * Get all documents from the spec
   * Returns a defensive copy to prevent mutation of internal state
   */
  getAllDocs(): DocInfo[] {
    return [...this.allDocs]; // Return a shallow copy to prevent mutation
  }

  /**
   * Get DocInfo for a specific content path.
   * Handles both paths with and without "docs/" prefix.
   */
  getDocInfoByPath(path: string): DocInfo | undefined {
    return (
      this.pathToDocInfo.get(`docs/${path}`) ?? this.pathToDocInfo.get(path)
    );
  }

  /**
   * Get the full doc specs
   */
  getFullSpec(): FullDocsSpec {
    return docsSpec;
  }
}

// Export the singleton instance
export const docRegistry = DocRegistry.getInstance();
