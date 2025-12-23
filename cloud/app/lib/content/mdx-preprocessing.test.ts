import { Effect } from "effect";
import {
  describe,
  expect,
  MockFileSystem,
  createContentTestUtils,
} from "@/tests/content";
import { preprocessMdx, inferLanguageFromPath } from "./mdx-preprocessing";
import { ContentError } from "./errors";

describe("mdx-preprocessing", () => {
  describe("inferLanguageFromPath", () => {
    // These are pure function tests, no mock needed
    const { it } = createContentTestUtils(new MockFileSystem());

    it("infers Python from .py extension", () => {
      expect(inferLanguageFromPath("/path/to/file.py")).toBe("python");
    });

    it("infers TypeScript from .ts extension", () => {
      expect(inferLanguageFromPath("/path/to/file.ts")).toBe("typescript");
    });

    it("infers JavaScript from .js extension", () => {
      expect(inferLanguageFromPath("/path/to/file.js")).toBe("javascript");
    });

    it("returns text for unknown extension", () => {
      expect(inferLanguageFromPath("/path/to/file.unknown")).toBe("text");
    });

    it("returns text for files without extension", () => {
      expect(inferLanguageFromPath("/path/to/file")).toBe("text");
    });
  });

  describe("preprocessMdx", () => {
    describe("basic file reading", () => {
      const mockFs = new MockFileSystem().addFile(
        "/content/docs/test.mdx",
        `---
title: Test Document
description: A test document
---

# Hello World

This is a test.`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("reads and parses a simple MDX file", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx("/content/docs/test.mdx");

          expect(result.frontmatter).toEqual({
            title: "Test Document",
            description: "A test document",
          });
          expect(result.content).toContain("# Hello World");
          expect(result.content).toContain("This is a test.");
          expect(result.fullContent).toContain("---");
        }),
      );
    });

    describe("CodeExample processing", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/content/docs/mirascope/guide.mdx",
          `---
title: Guide
description: A guide
---

# Guide

<CodeExample file="@/examples/hello.py" />`,
        )
        .addFile(
          "/content/docs/mirascope/examples/hello.py",
          `def hello():
    print("Hello, World!")`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("replaces CodeExample with actual code block", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/guide.mdx",
          );

          expect(result.fullContent).toContain("```python");
          expect(result.fullContent).toContain('print("Hello, World!")');
          expect(result.fullContent).not.toContain("<CodeExample");
        }),
      );
    });

    describe("CodeExample with line range", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/content/docs/mirascope/guide.mdx",
          `---
title: Guide
description: A guide
---

<CodeExample file="@/examples/multi.py" lines="2-3" />`,
        )
        .addFile(
          "/content/docs/mirascope/examples/multi.py",
          `# Line 1
# Line 2
# Line 3
# Line 4`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("extracts only the specified lines", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/guide.mdx",
          );

          expect(result.fullContent).toContain("# Line 2");
          expect(result.fullContent).toContain("# Line 3");
          expect(result.fullContent).not.toContain("# Line 1");
          expect(result.fullContent).not.toContain("# Line 4");
        }),
      );
    });

    describe("CodeExample with custom language", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/content/docs/mirascope/guide.mdx",
          `---
title: Guide
description: A guide
---

<CodeExample file="@/examples/code.txt" lang="javascript" />`,
        )
        .addFile(
          "/content/docs/mirascope/examples/code.txt",
          `console.log("hello");`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("uses the specified language", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/guide.mdx",
          );

          expect(result.fullContent).toContain("```javascript");
        }),
      );
    });

    describe("CodeExample with highlight", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/content/docs/mirascope/guide.mdx",
          `---
title: Guide
description: A guide
---

<CodeExample file="@/examples/code.py" highlight="1,3" />`,
        )
        .addFile(
          "/content/docs/mirascope/examples/code.py",
          `line1
line2
line3`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("includes highlight metadata", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/guide.mdx",
          );

          expect(result.fullContent).toContain("```python {1,3}");
        }),
      );
    });

    describe("error handling", () => {
      const mockFs = new MockFileSystem();
      const { it } = createContentTestUtils(mockFs);

      it.effect("fails when file does not exist", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx("/nonexistent.mdx").pipe(
            Effect.flip,
          );

          expect(result).toBeInstanceOf(ContentError);
          expect(result.message).toContain("/nonexistent.mdx");
        }),
      );
    });

    describe("CodeExample error handling", () => {
      const mockFs = new MockFileSystem().addFile(
        "/content/docs/mirascope/broken.mdx",
        `---
title: Broken
description: A broken doc
---

<CodeExample file="@/examples/missing.py" />`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("fails when CodeExample file does not exist", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/broken.mdx",
          ).pipe(Effect.flip);

          expect(result).toBeInstanceOf(ContentError);
          expect(result.message).toContain("missing.py");
        }),
      );
    });

    describe("multiple CodeExamples", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/content/docs/mirascope/multi.mdx",
          `---
title: Multi
description: Multiple examples
---

<CodeExample file="@/examples/first.py" />

Some text in between.

<CodeExample file="@/examples/second.ts" />`,
        )
        .addFile("/content/docs/mirascope/examples/first.py", `# First file`)
        .addFile(
          "/content/docs/mirascope/examples/second.ts",
          `// Second file`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("processes all CodeExamples", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx(
            "/content/docs/mirascope/multi.mdx",
          );

          expect(result.fullContent).toContain("```python");
          expect(result.fullContent).toContain("# First file");
          expect(result.fullContent).toContain("```typescript");
          expect(result.fullContent).toContain("// Second file");
          expect(result.fullContent).not.toContain("<CodeExample");
        }),
      );
    });

    describe("no frontmatter", () => {
      const mockFs = new MockFileSystem().addFile(
        "/content/docs/no-front.mdx",
        `# No Frontmatter

Just content.`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("handles files without frontmatter", () =>
        Effect.gen(function* () {
          const result = yield* preprocessMdx("/content/docs/no-front.mdx");

          expect(result.frontmatter).toEqual({});
          expect(result.content).toContain("# No Frontmatter");
        }),
      );
    });
  });
});
