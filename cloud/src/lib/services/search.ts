import { environment } from "../content/environment";
import { type ContentMeta } from "../content/content";
import { SearchScorer, type RawSearchResult, type SearchResultItem } from "./search-scoring";

// Define Pagefind types
interface PagefindResult {
  id: string;
  score: number;
  data: () => Promise<{
    url: string;
    excerpt: string;
    meta?: Record<string, string>;
    content: string;
  }>;
}

interface PagefindAPI {
  init: () => Promise<void>;
  search: (query: string) => Promise<{
    results: PagefindResult[];
  }>;
  debouncedSearch: (
    query: string,
    time?: number
  ) => Promise<{
    results: PagefindResult[];
  } | null>;
  options: (options: any) => Promise<void>;
}

// Re-export types from search-scoring for convenience
export type { SearchResultItem, RawSearchResult } from "./search-scoring";

export interface SearchResponse {
  items: SearchResultItem[];
}

// Search service interface
export interface SearchService {
  init(): Promise<void>; // Will reject with an error if initialization fails
  search(query: string): Promise<SearchResponse | null>; // Will reject with an error if search fails
  isInitialized(): boolean;
}

// Default section value when metadata is not available
const DEFAULT_SECTION = "other";

// Implementation of the search service using Pagefind
export class PagefindSearchService implements SearchService {
  private pagefind: PagefindAPI | null = null;
  private initialized = false;
  private contentMeta: ContentMeta[] = [];
  private routeToMetaMap: Map<string, ContentMeta> = new Map();
  private scorer: SearchScorer;

  constructor() {
    this.scorer = new SearchScorer();
  }

  async init(): Promise<void> {
    if (this.initialized) return;

    if (environment.isDev()) {
      console.log("🔍 [SearchService] Initializing Pagefind...");
    }

    // Check if we're running in a browser environment
    if (typeof window === "undefined") {
      throw new Error("Cannot initialize search in a non-browser environment");
    }

    try {
      // We need to run two initialization tasks in parallel:
      // 1. Load Pagefind search engine
      // 2. Load the unified content metadata
      await Promise.all([this.initPagefind(), this.loadContentMeta()]);

      this.initialized = true;
    } catch (error) {
      this.initialized = false;
      if (environment.isDev()) {
        console.error("🔍 [SearchService] Error during initialization:", error);
      }
      throw new Error(
        "Search initialization failed. Try running 'bun run build' to regenerate content."
      );
    }
  }

  /**
   * Initialize the Pagefind search engine
   */
  private async initPagefind(): Promise<void> {
    // Check if Pagefind is already loaded
    if (window.pagefind) {
      this.pagefind = window.pagefind;
      return;
    }

    try {
      const dynamicImport = new Function("url", "return import(url)");
      const pagefind = await dynamicImport("/_pagefind/pagefind.js");

      // Store pagefind on the window and local instance
      window.pagefind = pagefind;
      this.pagefind = pagefind;

      // Initialize Pagefind
      await pagefind.init();

      // Configure Pagefind
      await pagefind.options({
        baseUrl: "/",
      });

      if (environment.isDev()) {
        console.log("🔍 [SearchService] Pagefind loaded successfully");
      }
    } catch (error) {
      if (environment.isDev()) {
        console.error("🔍 [SearchService] Error loading Pagefind:", error);
      }
      throw new Error("Search index not available. Run 'bun run build' to generate it.");
    }
  }

  /**
   * Load the unified content metadata and build route map
   */
  private async loadContentMeta(): Promise<void> {
    try {
      if (environment.isDev()) {
        console.log("🔍 [SearchService] Loading content metadata...");
      }

      // Fetch the unified metadata file
      const response = await fetch("/static/content-meta/unified.json");

      if (!response.ok) {
        throw new Error(
          `Failed to load content metadata: ${response.status} ${response.statusText}`
        );
      }

      // Parse the JSON response
      this.contentMeta = await response.json();

      // Build the route to metadata map for quick lookups
      this.routeToMetaMap = new Map();
      for (const meta of this.contentMeta) {
        this.routeToMetaMap.set(meta.route, meta);
      }

      if (environment.isDev()) {
        console.log(`🔍 [SearchService] Loaded ${this.contentMeta.length} content metadata items`);
      }
    } catch (error) {
      if (environment.isDev()) {
        console.error("🔍 [SearchService] Error loading content metadata:", error);
      }
      throw new Error(
        "Content metadata not available. Try running 'bun run build' to regenerate content."
      );
    }
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  async search(query: string): Promise<SearchResponse | null> {
    // Handle empty queries
    if (!query.trim()) {
      return { items: [] };
    }

    // Check initialization
    if (!this.initialized || !this.pagefind) {
      throw new Error("Search engine not initialized");
    }

    // Use the built-in debouncedSearch with 300ms delay
    const result = await this.pagefind.debouncedSearch(query, 300);

    // If the search was cancelled (due to rapid typing), return null
    if (result === null) {
      return null;
    }

    if (environment.isDev()) {
      console.log(`🔍 [SearchService] Found ${result.results.length} results`);
    }

    // Process and transform all results
    // Get all result data in a single batch of promises
    const rawResults: RawSearchResult[] = await Promise.all(
      result.results.map(async (pagefindResult) => {
        const data = await pagefindResult.data();

        // Normalize the URL to match our routes
        let url = data.url || "";
        if (url.endsWith(".html")) {
          url = url.slice(0, -5);
        }

        // Try to find matching metadata using the URL as route
        const meta = this.findMetadataByUrl(url);

        // Log warning for documents without metadata
        if (!meta) {
          console.warn(`🔍 [SearchService] No metadata found for URL: ${url}`);
        }

        // Use metadata if found, otherwise fallback to Pagefind data
        const title = meta?.title || data.meta?.title || "Untitled";
        const excerpt = data.excerpt || "";
        const section = this.getSectionFromMeta(meta);

        // Create the raw search result
        const rawResult: RawSearchResult = {
          title,
          excerpt,
          url,
          section,
          score: pagefindResult.score || 0,
          meta, // May be undefined if no metadata found
        };

        return rawResult;
      })
    );

    // Apply custom scoring logic (will filter and transform raw results)
    const scoredItems = this.scorer.scoreAndRankResults(rawResults, query);

    // Log a summary of the top 5 results if in dev mode
    if (environment.isDev() && scoredItems.length > 0) {
      console.log(
        `🔍 [SearchService] Top ${Math.min(5, scoredItems.length)} results after scoring:`
      );
      scoredItems.slice(0, 5).forEach((item, index) => {
        console.log(
          `  ${index + 1}. ${item.title} (score: ${item.score.toFixed(3)}, raw: ${item.rawScore.toFixed(3)}, weight: ${item.weight}, type: ${item.meta.type})`
        );
      });
    }

    // Return the search response with scored items
    return { items: scoredItems };
  }

  /**
   * Finds the matching content metadata for a given URL
   * Handles URL normalization to match our route formats
   */
  private findMetadataByUrl(url: string): ContentMeta | undefined {
    // Normalize URL to handle potential differences
    let normalizedUrl = url;

    // Strip any domain part if present
    if (normalizedUrl.startsWith("http")) {
      try {
        normalizedUrl = new URL(normalizedUrl).pathname;
      } catch (e) {
        console.warn(`🔍 [SearchService] Failed to parse URL: ${url}`);
      }
    }

    // Ensure leading slash
    if (!normalizedUrl.startsWith("/")) {
      normalizedUrl = "/" + normalizedUrl;
    }

    // Remove trailing slash if present (except for root)
    if (normalizedUrl.endsWith("/") && normalizedUrl !== "/") {
      normalizedUrl = normalizedUrl.slice(0, -1);
    }

    // Try to find metadata by route
    const meta = this.routeToMetaMap.get(normalizedUrl);

    // If not found, try alternative versions of the URL
    if (!meta) {
      // Try with trailing slash
      if (!normalizedUrl.endsWith("/")) {
        const withSlash = normalizedUrl + "/";
        const metaWithSlash = this.routeToMetaMap.get(withSlash);
        if (metaWithSlash) return metaWithSlash;
      }

      // Try without trailing slash
      if (normalizedUrl.endsWith("/")) {
        const withoutSlash = normalizedUrl.slice(0, -1);
        const metaWithoutSlash = this.routeToMetaMap.get(withoutSlash);
        if (metaWithoutSlash) return metaWithoutSlash;
      }
    }

    return meta;
  }

  /**
   * Extract section name from content metadata
   */
  private getSectionFromMeta(meta: ContentMeta | undefined): string {
    // If no metadata is available, return the default section
    if (!meta) return DEFAULT_SECTION;

    // For blog, doc, policy, and dev, we can derive section from the content type
    switch (meta.type) {
      case "blog":
        return "blog";
      case "docs":
        // For docs, we want to show the full path up to the slug
        const docPath = meta.path.split("/").filter(Boolean);

        // If path has segments, display all except the last one (which is the slug)
        if (docPath.length > 1) {
          // Skip the 'doc' prefix, then take everything except the last segment
          const pathSegments = docPath.slice(1, -1);

          // If there are path segments, join them with slashes (keeping original case)
          if (pathSegments.length > 0) {
            return pathSegments.join("/");
          }

          // If there's just one segment after 'doc', use it as is (like 'mirascope')
          return docPath[1];
        }
        return "docs";
      case "policy":
        return "policy";
      case "dev":
        return "dev";
      default:
        return DEFAULT_SECTION;
    }
  }
}

// Create singleton instance
let searchServiceInstance: SearchService | null = null;

// Factory function to get the search service
export function getSearchService(): SearchService {
  if (!searchServiceInstance) {
    searchServiceInstance = new PagefindSearchService();
  }
  return searchServiceInstance;
}

// Declare Pagefind types on the window object
declare global {
  interface Window {
    pagefind?: PagefindAPI;
  }
}
