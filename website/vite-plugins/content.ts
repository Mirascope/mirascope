/**
 * Vite plugin for content meta management
 *
 * This plugin scans the content directory for MDX files and maintains
 * metadata about all content for listing and querying.
 *
 * Features:
 * - Scans content directory on startup
 * - Builds metadata for all MDX files (title, description, slug, etc.)
 * - Exposes meta via virtual:content-meta module
 * - Supports Hot Module Replacement (HMR) in development
 *
 * Usage:
 * ```typescript
 * import { blogPosts, allContent } from "virtual:content-meta";
 *
 * // blogPosts: BlogMeta[] - blog posts sorted by date (newest first)
 * // allContent: ContentMeta[] - all MDX content entries
 * ```
 */

import type { Plugin, ViteDevServer } from "vite";

import ContentProcessor from "../app/lib/content/content-processor";

const VIRTUAL_MODULE_ID = "virtual:content-meta";
// The "\0" prefix is a Vite convention that marks this as a virtual module,
// preventing Vite from trying to resolve it as a real file path
const RESOLVED_VIRTUAL_MODULE_ID = "\0" + VIRTUAL_MODULE_ID;

export interface ViteContentOptions {
  /** ContentProcessor instance to use (allows sharing across plugins during build) */
  processor: ContentProcessor;
}

/**
 * ContentExporter - Handles Vite-specific export generation for content metadata
 */
class ContentExporter {
  private readonly processor: ContentProcessor;

  constructor(processor: ContentProcessor) {
    this.processor = processor;
  }

  /**
   * Generate the virtual module export string for content metadata
   */
  generateExport(): string {
    if (!this.processor.isProcessed()) {
      throw new Error(
        "[vite-plugin-content] Content processor has not been run yet. " +
          "Metadata cannot be generated until content has been processed.",
      );
    }
    const metadata = this.processor.getMetadata();
    return `
    /** @type {import('../app/lib/content/types').BlogMeta[]} */
    export const blogMetadata = ${JSON.stringify(metadata.blog)};
    /** @type {import('../app/lib/content/types').DocMeta[]} */
    export const docsMetadata = ${JSON.stringify(metadata.docs)};
    /** @type {import('../app/lib/content/types').PolicyMeta[]} */
    export const policyMetadata = ${JSON.stringify(metadata.policy)};
    /** @type {import('../app/lib/content/types').DevMeta[]} */
    export const devMetadata = ${JSON.stringify(metadata.dev)};
    `.trim();
  }
}

export function viteContent(options: ViteContentOptions): Plugin {
  if (!options.processor) {
    throw new Error(
      "[vite-plugin-content] processor option is required and must be a ContentProcessor instance",
    );
  }

  const processor = options.processor;
  const exporter = new ContentExporter(processor);
  let isBuild = false;
  let serverInstance: ViteDevServer | null = null;

  // Debounced processing for HMR - prevents rapid-fire reprocessing
  // when multiple files change in quick succession (e.g., git operations, autosave)
  const debouncedProcessAndInvalidate = debounce(async () => {
    await processor.processAllContent({ failOnError: false, rerun: true });

    // Invalidate the virtual meta module after processing
    if (serverInstance) {
      const metaModule = serverInstance.moduleGraph.getModuleById(
        RESOLVED_VIRTUAL_MODULE_ID,
      );
      if (metaModule) {
        serverInstance.moduleGraph.invalidateModule(metaModule);
      }
    }
  }, 200);

  return {
    name: "vite-plugin-content",

    // Detect build vs serve mode
    config(_config, { command }) {
      isBuild = command === "build";
    },

    async configureServer(server) {
      serverInstance = server;
      // Scan content directory on startup
      await debouncedProcessAndInvalidate();
    },

    async buildStart() {
      // Scan content directory during build (only in build mode)
      if (!isBuild) {
        return;
      }
      await processor.processAllContent();
    },

    // Resolve virtual module imports
    resolveId(id) {
      if (id === VIRTUAL_MODULE_ID) {
        return RESOLVED_VIRTUAL_MODULE_ID;
      }
    },

    // Load the virtual module content
    load(id) {
      if (id === RESOLVED_VIRTUAL_MODULE_ID) {
        return exporter.generateExport();
      }
    },

    // Watch for file additions and deletions
    watchChange(id, { event }) {
      if (!processor.isRelevantMdxFile(id)) {
        return;
      }
      if (event === "create" || event === "delete") {
        console.log(`[content] File ${event}: ${id}`);
        void debouncedProcessAndInvalidate();
      }
    },

    // Enable HMR for content meta updates (modifications)
    async handleHotUpdate({ file }) {
      if (!processor.isRelevantMdxFile(file)) {
        return;
      }
      console.log(`[content] Updating meta for ${file}`);
      await debouncedProcessAndInvalidate();
    },
  };
}

/**
 * Creates a debounced version of an async function.
 * Multiple calls within the delay period will only execute once after the delay.
 * If processing is already running when the timer fires, it will queue another run
 * after the current one completes.
 */
function debounce<T extends (...args: unknown[]) => Promise<void>>(
  fn: T,
  ms: number,
): (...args: Parameters<T>) => Promise<void> {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let isProcessing = false;
  let queuedExecution: { args: Parameters<T>; resolve: () => void } | null =
    null;

  const execute = async (args: Parameters<T>): Promise<void> => {
    if (isProcessing) {
      // Return a promise that will resolve when this queued work actually completes
      return new Promise<void>((resolve) => {
        // If there's already a queued execution, replace args (debounce behavior)
        queuedExecution = { args, resolve };
      });
    }

    isProcessing = true;
    try {
      await fn(...args);
    } finally {
      isProcessing = false;
      timeoutId = null;

      // Process queued execution
      if (queuedExecution) {
        const { args: queuedArgs, resolve } = queuedExecution;
        queuedExecution = null;
        await fn(...queuedArgs);
        resolve();
      }
    }
  };

  return (...args: Parameters<T>): Promise<void> => {
    if (timeoutId) clearTimeout(timeoutId);

    const promise = new Promise<void>((resolve) => {
      timeoutId = setTimeout(() => {
        void execute(args).then(resolve);
      }, ms);
    });

    return promise;
  };
}
