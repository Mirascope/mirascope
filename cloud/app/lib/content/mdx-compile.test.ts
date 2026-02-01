import { describe, it, expect, beforeEach, vi } from "vitest";

import { compileMDXContent } from "./mdx-compile";

describe("compileMDXContent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should compile basic MDX content to function body code", async () => {
    const content = "# Hello World\n\nThis is a test.";
    const result = await compileMDXContent(content);

    // Result should be a string containing compiled JSX code
    expect(typeof result).toBe("string");
    expect(result).toContain("Hello World");
    // function-body format uses _jsx/_jsxs instead of exports
    expect(result).toContain("_jsx");
  });

  it("should compile MDX content with frontmatter (frontmatter is passed through)", async () => {
    // The compileMDXContent function receives content WITH frontmatter still in it
    const rawContent = `---
title: Test Post
description: A test description
date: 2025-01-01
---

# Test Content

This is the body.`;

    const result = await compileMDXContent(rawContent);

    // Frontmatter should NOT appear in compiled output (MDX strips it)
    expect(result).toContain("Test Content");
    expect(result).toContain("_jsx");
  });

  it("should compile empty content", async () => {
    const result = await compileMDXContent("");

    expect(typeof result).toBe("string");
    expect(result).toBeDefined();
  });

  it("should compile content with only frontmatter", async () => {
    const rawContent = `---
title: Only Frontmatter
---

`;

    const result = await compileMDXContent(rawContent);

    expect(typeof result).toBe("string");
    expect(result).toBeDefined();
  });

  it("should compile MDX with code blocks", async () => {
    const content = `# Code Example

\`\`\`typescript
const x = 1;
\`\`\`

More text.`;

    const result = await compileMDXContent(content);

    expect(typeof result).toBe("string");
    expect(result).toContain("Code Example");
  });

  it("should compile MDX with lists", async () => {
    const content = `# List Example

- Item 1
- Item 2
  - Nested item

1. Numbered item
2. Another item`;

    const result = await compileMDXContent(content);

    expect(result).toContain("List Example");
  });

  it("should compile MDX with links and images", async () => {
    const content = `# Links

[Link text](https://example.com)

![Alt text](/image.png)`;

    const result = await compileMDXContent(content);

    expect(result).toContain("Links");
    expect(result).toContain("https://example.com");
  });

  it("should compile code blocks with language identifiers", async () => {
    const content = `\`\`\`typescript
const x = 1;
\`\`\``;

    const result = await compileMDXContent(content);

    expect(typeof result).toBe("string");
    // The code should compile with the language identifier preserved
    expect(result).toContain("typescript");
  });

  it("should compile GFM tables", async () => {
    const content = `# Table Example

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |`;

    const result = await compileMDXContent(content);

    expect(result).toContain("Table Example");
  });

  it("should compile GFM strikethrough", async () => {
    const content = `# Strikethrough

~~deleted text~~`;

    const result = await compileMDXContent(content);

    expect(result).toContain("Strikethrough");
  });

  it("should produce function-body format output", async () => {
    const content = "# Test";
    const result = await compileMDXContent(content);

    // function-body format characteristics:
    // - Uses arguments[0] for runtime dependencies
    // - Has _jsx/_jsxs calls
    // - Does NOT have ES module imports/exports
    expect(result).not.toMatch(/^import\s/m);
    expect(result).not.toMatch(/^export\s/m);
  });
});
