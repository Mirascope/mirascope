/**
 * Tests for static rendering utilities
 */

import { describe, test, expect } from "bun:test";
const { renderRouteToString, createHtmlDocument } =
  await import("../static-renderer");

describe("Static Renderer", () => {
  // This test renders an actual route and verifies expected metadata
  test("renderRouteToString renders index route with correct metadata", async () => {
    // Import only when we need it to avoid side effects
    // Render the index route
    const result = await renderRouteToString("/");

    // Verify structure
    expect(result).toBeDefined();
    expect(result.html).toBeDefined();
    expect(result.metadata).toBeDefined();

    // Verify metadata contents
    expect(result.metadata.title).toBe("Home | Mirascope");
    expect(result.metadata.description).toBe(
      "The AI Engineer's Developer Stack",
    );

    // Verify meta tags include important SEO tags
    expect(result.metadata.meta).toContain("og:title");
    expect(result.metadata.meta).toContain("og:description");
    expect(result.metadata.meta).toContain("twitter:card");
  });

  test("renders home route with mirascope product attribute", async () => {
    // Render the index route
    const result = await renderRouteToString("/");

    // Verify the data-product attribute is set to "mirascope" on the root div
    expect(result.html).toContain('<div data-product="mirascope"');
  });

  test("renders pricing route with lilypad product attribute", async () => {
    // Render the pricing route
    const result = await renderRouteToString("/pricing");

    // Verify the data-product attribute is set to "lilypad" on the root div
    expect(result.html).toContain('<div data-product="lilypad"');
  });

  test("blog posts include Article schema JSON-LD", async () => {
    // Render a blog post
    const result = await renderRouteToString("/blog/llm-integration");

    // Verify metadata has jsonLdScripts
    expect(result.metadata.jsonLdScripts).toBeDefined();

    // Verify the Article schema is included in the JSON-LD scripts
    expect(result.metadata.jsonLdScripts).toContain("application/ld+json");
    expect(result.metadata.jsonLdScripts).toContain('"@type":"Article"');
    expect(result.metadata.jsonLdScripts).toContain(
      '"@context":"https://schema.org"',
    );

    // Verify specific fields are present in the metadata
    expect(result.metadata.jsonLdScripts).toContain('"headline"');
    expect(result.metadata.jsonLdScripts).toContain('"description"');
    expect(result.metadata.jsonLdScripts).toContain('"image"');
    expect(result.metadata.jsonLdScripts).toContain('"url"');
    expect(result.metadata.jsonLdScripts).toContain('"author"');

    // Create a full HTML document from the rendered route
    const fullHtml = createHtmlDocument(result.html, result.metadata);

    // Verify the script tag is injected into the final HTML document
    expect(fullHtml).toContain('<script type="application/ld+json">');
    expect(fullHtml).toContain('"@type":"Article"');
    expect(fullHtml).toContain('"@context":"https://schema.org"');

    // Verify canonical URL is included in the link tags
    expect(result.metadata.link).toContain('<link rel="canonical"');
    expect(result.metadata.link).toContain("/blog/llm-integration");
    expect(fullHtml).toContain('<link rel="canonical"');

    // Ensure canonical URL doesn't have a trailing slash
    expect(result.metadata.link).not.toContain("/blog/llm-integration/");
  });
});
