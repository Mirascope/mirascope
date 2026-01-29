/**
 * DocRegistry - A singleton service for efficient document information management
 *
 * Canonical doc info, fast lookups, section/weight hierarchy.
 * Note: Cannot use import aliases in this file.
 */

import { docsSpec } from "@/../content/docs/_meta";

import type { FullDocsSpec, DocInfo } from "./spec";

import { getDocsFromSpec } from "./spec";

/**
 * DocRegistry service - Singleton for efficient document information management
 */
class DocRegistry {
  private static instance: DocRegistry;

  // List of all docs from the spec
  private readonly allDocs: DocInfo[];

  // Path lookup maps for efficient querying
  private readonly pathToDocInfo: Map<string, DocInfo>;
  private readonly routePathToDocInfo: Map<string, DocInfo>;

  private constructor() {
    // Initialize lookups
    this.pathToDocInfo = new Map();
    this.routePathToDocInfo = new Map();

    // Process the full docs spec to generate all DocInfo objects
    this.allDocs = getDocsFromSpec(docsSpec);

    // Build lookup maps for efficient access
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
   * Builds efficient lookup maps for paths and route paths
   */
  private buildLookupMaps(): void {
    for (const docInfo of this.allDocs) {
      // Map content paths to DocInfo (for content loading)
      this.pathToDocInfo.set(docInfo.path, docInfo);

      // Map route paths to DocInfo (for URL routing)
      this.routePathToDocInfo.set(docInfo.routePath, docInfo);

      // Also add versions with and without trailing slashes for robustness
      if (docInfo.routePath.endsWith("/")) {
        this.routePathToDocInfo.set(docInfo.routePath.slice(0, -1), docInfo);
      } else {
        this.routePathToDocInfo.set(docInfo.routePath + "/", docInfo);
      }
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
   * Get DocInfo for a specific content path
   */
  getDocInfoByPath(path: string): DocInfo | undefined {
    return this.pathToDocInfo.get(path);
  }

  /**
   * Get DocInfo for a specific route path
   */
  getDocInfoByRoutePath(routePath: string): DocInfo | undefined {
    return this.routePathToDocInfo.get(routePath);
  }

  //   /**
  //    * Get all doc specs from a particular product and section
  //    */
  //   getDocsInSection(product: Product, sectionSlug: string): DocInfo[] {
  //     const productSpec = this.getProductSpec(product);
  //     if (!productSpec) return [];

  //     const section = productSpec.sections.find((s) => s.slug === sectionSlug);
  //     if (!section) return [];

  //     const isDefaultSection = section.slug === "index";

  //     const basePathPrefix = productKey(product);
  //     const sectionPathPrefix = isDefaultSection
  //       ? basePathPrefix
  //       : `${basePathPrefix}/${section.slug}`;

  //     // Flatten the section hierarchy
  //     const result: DocInfo[] = [];
  //     section.children.forEach((docSpec) => {
  //       const docItems = processDocSpec(docSpec, product, sectionPathPrefix);
  //       result.push(...docItems);
  //     });

  //     return result;
  //   }

  /**
   * Get the full doc specs
   */
  getFullSpec(): FullDocsSpec {
    return docsSpec;
  }
}

// Export the singleton instance
export const docRegistry = DocRegistry.getInstance();
