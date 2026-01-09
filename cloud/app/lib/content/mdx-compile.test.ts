import { describe, it, expect, beforeEach, vi } from "vitest";
import { compileMDXContent, createProcessedMDX } from "./mdx-compile";
import type { Frontmatter } from "@/app/lib/mdx/types";
import type { TOCItem } from "@/app/lib/content/types";

describe("compileMDXContent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should compile basic MDX content without frontmatter", async () => {
    const content = "# Hello World\n\nThis is a test.";
    const result = await compileMDXContent(content);

    expect(result.content).toBe(content);
    expect(result.frontmatter).toEqual({});
    expect(result.tableOfContents).toEqual([
      { id: "hello-world", text: "Hello World", level: 1 },
    ]);
    expect(result.jsxCode).toContain("Hello World");
    expect(result.jsxCode).toContain("MDXContent");
  });

  it("should parse frontmatter and compile content", async () => {
    const rawContent = `---
title: Test Post
description: A test description
date: 2025-01-01
---

# Test Content

This is the body.`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Test Post",
      description: "A test description",
      date: "2025-01-01",
    });
    expect(result.content).toBe("# Test Content\n\nThis is the body.");
    expect(result.tableOfContents).toEqual([
      { id: "test-content", text: "Test Content", level: 1 },
    ]);
    expect(result.jsxCode).toContain("Test Content");
    expect(result.jsxCode).toContain("MDXContent");
  });

  it("should extract table of contents from headings", async () => {
    const content = `# Main Title

## Section One

### Subsection 1.1

## Section Two

### Subsection 2.1

#### Sub-subsection 2.1.1`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "main-title", text: "Main Title", level: 1 },
      { id: "section-one", text: "Section One", level: 2 },
      { id: "subsection-1-1", text: "Subsection 1.1", level: 3 },
      { id: "section-two", text: "Section Two", level: 2 },
      { id: "subsection-2-1", text: "Subsection 2.1", level: 3 },
      { id: "sub-subsection-2-1-1", text: "Sub-subsection 2.1.1", level: 4 },
    ]);
  });

  it("should remove default export from compiled JSX", async () => {
    const content = "# Test";
    const result = await compileMDXContent(content);

    // Should not contain any default export statements
    expect(result.jsxCode).not.toMatch(/export\s+default\s+MDXContent/);
    expect(result.jsxCode).not.toMatch(/export\s+default\s+MDXContent;/);
  });

  it("should handle empty content", async () => {
    const result = await compileMDXContent("");

    expect(result.content).toBe("");
    expect(result.frontmatter).toEqual({});
    expect(result.tableOfContents).toEqual([]);
    expect(result.jsxCode).toBeDefined();
  });

  it("should handle content with only frontmatter", async () => {
    const rawContent = `---
title: Only Frontmatter
---

`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Only Frontmatter",
    });
    expect(result.content.trim()).toBe("");
    expect(result.tableOfContents).toEqual([]);
  });

  it("should handle frontmatter with quoted values", async () => {
    const rawContent = `---
title: "Quoted Title"
description: 'Single quoted description'
---

# Content`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Quoted Title",
      description: "Single quoted description",
    });
  });

  it("should compile MDX with code blocks", async () => {
    const content = `# Code Example

\`\`\`typescript
const x = 1;
\`\`\`

More text.`;

    const result = await compileMDXContent(content);

    expect(result.content).toBe(content);
    expect(result.tableOfContents).toEqual([
      { id: "code-example", text: "Code Example", level: 1 },
    ]);
    expect(result.jsxCode).toContain("Code Example");
  });

  it("should compile MDX with lists", async () => {
    const content = `# List Example

- Item 1
- Item 2
  - Nested item

1. Numbered item
2. Another item`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "list-example", text: "List Example", level: 1 },
    ]);
    expect(result.jsxCode).toContain("List Example");
  });

  it("should compile MDX with links and images", async () => {
    const content = `# Links

[Link text](https://example.com)

![Alt text](/image.png)`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "links", text: "Links", level: 1 },
    ]);
    expect(result.jsxCode).toContain("Links");
  });

  it("should skip syntax highlighting when skipHighlighting is true", async () => {
    const content = `\`\`\`typescript
const x = 1;
\`\`\``;

    const result = await compileMDXContent(content, { skipHighlighting: true });

    expect(result.jsxCode).toBeDefined();
    // The code should still compile, just without syntax highlighting
    expect(result.jsxCode).toContain("typescript");
  });

  it("should include syntax highlighting by default", async () => {
    const content = `\`\`\`typescript
const x = 1;
\`\`\``;

    const result = await compileMDXContent(content);

    expect(result.jsxCode).toBeDefined();
    // With highlighting, the output structure may differ
    expect(result.jsxCode).toContain("typescript");
  });

  it("should handle frontmatter with empty values", async () => {
    const rawContent = `---
title: Test
description:
date: 2025-01-01
---

# Content`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Test",
      description: "",
      date: "2025-01-01",
    });
  });

  it("should handle multiple frontmatter fields", async () => {
    const rawContent = `---
title: Multi Field
author: Test Author
date: 2025-01-01
category: Tech
tags: test, mdx
---

# Content`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Multi Field",
      author: "Test Author",
      date: "2025-01-01",
      category: "Tech",
      tags: "test, mdx",
    });
  });

  it("should handle headings with special characters in TOC", async () => {
    const content = `# Hello, World!
## Test & Example
### What's Next?`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "hello-world", text: "Hello, World!", level: 1 },
      { id: "test-example", text: "Test & Example", level: 2 },
      { id: "what-s-next", text: "What's Next?", level: 3 },
    ]);
  });

  it("should handle content with GFM features (tables)", async () => {
    const content = `# Table Example

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "table-example", text: "Table Example", level: 1 },
    ]);
    expect(result.jsxCode).toContain("Table Example");
  });

  it("should handle content with strikethrough (GFM)", async () => {
    const content = `# Strikethrough

~~deleted text~~`;

    const result = await compileMDXContent(content);

    expect(result.tableOfContents).toEqual([
      { id: "strikethrough", text: "Strikethrough", level: 1 },
    ]);
  });

  it("should handle malformed frontmatter gracefully", async () => {
    const rawContent = `---
title: Test
invalid line without colon
date: 2025-01-01
---

# Content`;

    const result = await compileMDXContent(rawContent);

    // Should still parse valid frontmatter fields
    expect(result.frontmatter).toEqual({
      title: "Test",
      date: "2025-01-01",
    });
  });

  it("should handle frontmatter with colons in values", async () => {
    const rawContent = `---
title: Test: With Colon
time: 10:30 AM
---

# Content`;

    const result = await compileMDXContent(rawContent);

    expect(result.frontmatter).toEqual({
      title: "Test: With Colon",
      time: "10:30 AM",
    });
  });
});

describe("createProcessedMDX", () => {
  it("should create a ProcessedMDX component with metadata", () => {
    const content = "# Test Content";
    const frontmatter: Frontmatter = {
      title: "Test",
      description: "A test",
    };
    const tableOfContents: TOCItem[] = [
      { id: "test-content", text: "Test Content", level: 1 },
    ];

    const processed = createProcessedMDX(content, frontmatter, tableOfContents);

    expect(processed.content).toBe(content);
    expect(processed.frontmatter).toEqual(frontmatter);
    expect(processed.tableOfContents).toEqual(tableOfContents);
  });

  it("should create a component that renders null", () => {
    const processed = createProcessedMDX("", {});

    // Component should be callable and return null
    // createProcessedMDX returns a function component, so we assert it's callable
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
    const result = (processed as any)({});
    expect(result).toBeNull();
  });

  it("should use empty TOC array as default", () => {
    const processed = createProcessedMDX("content", { title: "Test" });

    expect(processed.tableOfContents).toEqual([]);
  });

  it("should handle empty frontmatter", () => {
    const processed = createProcessedMDX("content", {});

    expect(processed.frontmatter).toEqual({});
    expect(processed.content).toBe("content");
  });

  it("should handle complex frontmatter", () => {
    const frontmatter: Frontmatter = {
      title: "Complex",
      description: "Test",
      date: "2025-01-01",
      author: "Author",
      tags: ["tag1", "tag2"],
      custom: { nested: "value" },
    };

    const processed = createProcessedMDX("content", frontmatter);

    expect(processed.frontmatter).toEqual(frontmatter);
  });

  it("should handle complex TOC structure", () => {
    const toc: TOCItem[] = [
      {
        id: "main",
        text: "Main",
        level: 1,
        children: [{ id: "sub", text: "Sub", level: 2 }],
      },
    ];

    const processed = createProcessedMDX("content", {}, toc);

    expect(processed.tableOfContents).toEqual(toc);
  });

  it("should be assignable as ProcessedMDX type", () => {
    const processed = createProcessedMDX("content", { title: "Test" });

    // Type check: should have all required properties
    expect(processed).toHaveProperty("content");
    expect(processed).toHaveProperty("frontmatter");
    expect(processed).toHaveProperty("tableOfContents");
    expect(typeof processed).toBe("function");
  });
});
