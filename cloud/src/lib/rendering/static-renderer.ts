/**
 * Static Rendering Utilities
 *
 * Shared functionality for rendering React components to static HTML
 * and extracting metadata from the document head.
 */

import fs from "fs";
import path from "path";
import React from "react";
import { renderToString } from "react-dom/server";
import {
  createMemoryHistory,
  createRouter,
  RouterProvider,
} from "@tanstack/react-router";
import { routeTree } from "../../routeTree.gen";
import { environment } from "../content/environment";

// Import utilities for metadata extraction and rendering
import {
  deserializeMetadata,
  unifyMetadata,
} from "@/src/components/core/meta/utils";
import { generateMetadataHtml } from "@/src/components/core/meta/renderer";
import type { PageMetadata, RenderResult } from "./types";
import type { UnifiedMetadata } from "@/src/components/core/meta/types";

/**
 * Static fetch implementation for server-side rendering
 * Handles file paths and content loading
 */
export async function staticFetch(url: string) {
  // Handle content paths based on the URL
  let contentPath = url;

  // For paths that start with /, add the public directory
  if (url.startsWith("/")) {
    contentPath = path.join(process.cwd(), "public", url);
  }

  // Check if the file exists
  if (!fs.existsSync(contentPath)) {
    const error = new Error(`File not found: ${contentPath}`);
    environment.onError(error);
    throw error;
  }

  // Read the file content
  const content = fs.readFileSync(contentPath, "utf-8");

  // Determine the content type
  const isJson = contentPath.endsWith(".json");

  // Return a minimal response-like object
  return {
    ok: true,
    status: 200,
    statusText: "OK",
    text: async () => content,
    json: async () => (isJson ? JSON.parse(content) : { content }),
  };
}

/**
 * Configures the environment for static rendering
 */
export function configureStaticEnvironment() {
  // Initialize HappyDOM for server-side rendering if not already loaded
  if (typeof window === "undefined" && typeof document === "undefined") {
    // HappyDOM is expected to be loaded globally via happydom.ts
    // This will make document, window, etc. available
    // We don't need to do anything here because GlobalRegistrator.register() is called in happydom.ts
    require("@/happydom");
  }

  // @ts-ignore
  environment.fetch = staticFetch;
  environment.isDev = () => false;
  environment.isProd = () => true;
  environment.isPrerendering = true;

  return environment;
}

/**
 * Extract metadata from serialized divs in the rendered HTML
 * Ensures there is exactly one instance of each serialized metadata div
 */
export function extractSerializedMetadata(html: string): UnifiedMetadata {
  // Extract all instances of serialized metadata
  const coreMetaMatches = html.match(/data-core-meta="([^"]*)"/g);
  const routeMetaMatches = html.match(/data-route-meta="([^"]*)"/g);

  // Validate core metadata
  if (!coreMetaMatches) {
    throw new Error("Failed to extract core metadata from rendered HTML");
  }

  if (coreMetaMatches.length > 1) {
    throw new Error(
      `Found ${coreMetaMatches.length} instances of core metadata, expected exactly 1`,
    );
  }

  // Validate route metadata
  if (!routeMetaMatches) {
    throw new Error("Failed to extract route metadata from rendered HTML");
  }

  if (routeMetaMatches.length > 1) {
    throw new Error(
      `Found ${routeMetaMatches.length} instances of route metadata, expected exactly 1`,
    );
  }

  // Extract the actual encoded strings
  const coreMetaEncodedMatch = coreMetaMatches[0].match(
    /data-core-meta="([^"]*)"/,
  );
  const routeMetaEncodedMatch = routeMetaMatches[0].match(
    /data-route-meta="([^"]*)"/,
  );

  if (!coreMetaEncodedMatch || !coreMetaEncodedMatch[1]) {
    throw new Error("Failed to extract core metadata encoded string");
  }

  if (!routeMetaEncodedMatch || !routeMetaEncodedMatch[1]) {
    throw new Error("Failed to extract route metadata encoded string");
  }

  const coreMetaEncoded = coreMetaEncodedMatch[1];
  const routeMetaEncoded = routeMetaEncodedMatch[1];

  // Deserialize the metadata
  const coreMetadata = deserializeMetadata(coreMetaEncoded);
  const routeMetadata = deserializeMetadata(routeMetaEncoded);

  // Unify the metadata
  return unifyMetadata(coreMetadata, routeMetadata);
}

/**
 * Renders a React route to a string and extracts metadata
 *
 * @param route The route to render (e.g., "/privacy")
 * @param verbose Whether to log detailed information
 * @returns The rendered HTML string and extracted metadata
 */
export async function renderRouteToString(
  route: string,
): Promise<RenderResult> {
  // Configure environment
  const env = configureStaticEnvironment();
  let loadError: Error | null = null;

  env.onError = (error: Error) => {
    loadError = error;
  };

  // Create a memory history for the specified route
  const memoryHistory = createMemoryHistory({
    initialEntries: [route],
  });

  // Create a router instance for the route
  const router = createRouter({
    routeTree,
    history: memoryHistory,
    context: {
      environment: env,
    },
  });

  // Actually load the data and the component
  await router.load();

  // Router will catch errors, but if the error was properly
  // wired to the environment handler, then we can throw it
  // and correctly signal that the component failed to load
  if (loadError) {
    throw loadError;
  }

  const originalError = console.error;
  let renderError: unknown[] = [];
  console.error = (...args: unknown[]) => {
    renderError = [...args];
  };
  // Render the app to a string
  const appHtml = renderToString(
    React.createElement(RouterProvider, { router }),
  );
  console.error = originalError;

  // Check for the React client rendering fallback error in the output
  if (
    appHtml.includes(
      "Switched to client rendering because the server rendering errored",
    )
  ) {
    // Extract both the detailed error message and stack trace
    const templateElement = appHtml.match(
      /<template data-msg="([^"]*)"(?:\s+data-stck="([^"]*)")?[^>]*>/,
    );

    let errorMessage =
      "Fatal SSR error: React switched to client rendering fallback. This must be fixed before deployment.";

    if (templateElement) {
      // The error message is in capture group 1
      if (templateElement[1]) {
        const errorMsg = templateElement[1].replace(/\\n/g, "\n");
        errorMessage += `\n\nDetailed error message:\n${errorMsg}`;
      }

      // The stack trace is in capture group 2
      if (templateElement[2]) {
        const stackTrace = templateElement[2].replace(/\\n/g, "\n");
        errorMessage += `\n\nStack trace:\n${stackTrace}`;
      }
    } else {
      errorMessage += "\n\nNo detailed error information available.";
    }

    console.error(errorMessage);
    throw new Error(errorMessage);
  }

  if (renderError.length > 0) {
    console.error("Error rendering app:", ...renderError);
    throw new Error("Error rendering: " + renderError.join(" "));
  }
  // Extract metadata from serialized divs
  try {
    // Extract and unify metadata from serialized divs
    const unifiedMetadata = extractSerializedMetadata(appHtml);

    // Generate HTML for the metadata using our DOM-based renderer
    const metadataHtml = generateMetadataHtml(unifiedMetadata);

    // Create metadata object for the page
    const metadata: PageMetadata = {
      title: unifiedMetadata.title,
      description: unifiedMetadata.description,
      meta: metadataHtml.meta,
      link: metadataHtml.link,
      jsonLdScripts: metadataHtml.script,
    };

    return { html: appHtml, metadata };
  } catch (err) {
    const error = err as Error;
    console.error("Error extracting metadata:", error);
    throw new Error(`Failed to extract metadata: ${error.message}`);
  }
}

/**
 * Creates full HTML document with rendered content and metadata
 */
export function createHtmlDocument(
  renderedApp: string,
  metadata: PageMetadata,
  templatePath: string = path.join(process.cwd(), "index.html"),
): string {
  // Start with the original template
  let html = fs.readFileSync(templatePath, "utf-8");

  // Inject all metadata before </head>
  // The HTML will already include data-head-manager attributes from generateMetadataHtml
  html = html.replace(
    "</head>",
    `<title data-head-manager="true">${metadata.title}</title>
    ${metadata.meta}
    ${metadata.link}
    ${metadata.jsonLdScripts}
  </head>`,
  );

  // Replace app div content with pre-rendered HTML
  html = html.replace(
    '<div id="app"></div>',
    `<div id="app">${renderedApp}</div>`,
  );

  return html;
}
