/**
 * DocRegistry - A singleton service for efficient document information management
 *
 * This provides a canonical source for document information with efficient
 * lookups and hierarchical path management for sections and weights.
 */

import type {
  FullDocsSpec,
  Product,
  DocInfo,
  ProductName,
  ProductSpec,
  SectionSpec,
  DocSpec,
  ProductKey,
} from "./spec";
import { productKey, getDocsFromSpec, processDocSpec } from "./spec";

// Import the spec using relative path to avoid SSR path resolution issues
// From src/lib/content/ to content/ = ../../../content/
import fullSpecImport from "../../../content/docs/_meta";

// Use the imported spec, with fallback to empty array if import fails
let fullSpec: FullDocsSpec = [];
try {
  fullSpec = fullSpecImport;
} catch {
  // If import fails, use empty array - will be populated later if needed
  fullSpec = [];
}

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

  // Product information
  private readonly productMap: Map<ProductKey, ProductSpec>;

  private constructor() {
    // Initialize lookups
    this.pathToDocInfo = new Map();
    this.routePathToDocInfo = new Map();
    this.productMap = new Map();

    // Use the spec
    const spec = fullSpec;

    // Process the full docs spec to generate all DocInfo objects
    this.allDocs = getDocsFromSpec(spec);

    // Store product specs for access
    spec.forEach((productSpec) => {
      this.productMap.set(productKey(productSpec.product), productSpec);
    });

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

  public products(): Product[] {
    return Array.from(this.productMap.values()).map((p) => p.product);
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

  /**
   * Get all docs for a specific product
   */
  getDocsByProduct(product: Product): DocInfo[] {
    return this.allDocs.filter((doc) => productKey(doc.product) === productKey(product));
  }

  /**
   * Get the raw product specification
   */
  getProductSpec(product: Product): ProductSpec | undefined {
    return this.productMap.get(productKey(product));
  }

  /**
   * Get all doc specs from a particular product and section
   */
  getDocsInSection(product: Product, sectionSlug: string): DocInfo[] {
    const productSpec = this.getProductSpec(product);
    if (!productSpec) return [];

    const section = productSpec.sections.find((s) => s.slug === sectionSlug);
    if (!section) return [];

    const isDefaultSection = section.slug === "index";

    const basePathPrefix = productKey(product);
    const sectionPathPrefix = isDefaultSection
      ? basePathPrefix
      : `${basePathPrefix}/${section.slug}`;

    // Flatten the section hierarchy
    const result: DocInfo[] = [];
    section.children.forEach((docSpec) => {
      const docItems = processDocSpec(docSpec, product, sectionPathPrefix);
      result.push(...docItems);
    });

    return result;
  }

  /**
   * Get the full doc specs
   */
  getFullSpec(): FullDocsSpec {
    return fullSpec || [];
  }
}

// Export the singleton instance - initialization is lazy via getInstance()
export const docRegistry = DocRegistry.getInstance();

// Re-export types for convenience
export type { DocInfo, ProductName, ProductSpec, SectionSpec, DocSpec };
