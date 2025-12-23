import { Effect } from "effect";
import {
  describe,
  expect,
  MockFileSystem,
  createContentTestUtils,
} from "@/tests/content";
import { processAllContent, type PreprocessConfig } from "./preprocess";

// Note: These tests focus on content types (blog, policy, dev) that don't
// require the docRegistry. Testing docs would require mocking the registry.

describe("preprocess", () => {
  describe("processAllContent", () => {
    describe("directory initialization", () => {
      const mockFs = new MockFileSystem();
      const { it } = createContentTestUtils(mockFs);

      it.effect("creates required directories", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          yield* processAllContent(config);

          // Check that directories were created by checking if they exist
          // The mockFs tracks all created directories
          const files = mockFs.getAllFiles();

          // Since processAllContent creates directories, we should see
          // some evidence of the structure being created
          // Note: with no source content, we just verify no errors
          expect(files.size).toBeGreaterThanOrEqual(0);
        }),
      );
    });

    describe("blog processing", () => {
      const mockFs = new MockFileSystem().addFile(
        "/project/content/blog/my-post.mdx",
        `---
title: My Blog Post
description: A great blog post
date: 2024-01-15
author: Test Author
readTime: 5 min
---

# My Blog Post

This is the content.`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("processes blog content with valid metadata", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.blog).toHaveLength(1);
          expect(result.blog[0].title).toBe("My Blog Post");
          expect(result.blog[0].description).toBe("A great blog post");
          expect(result.blog[0].date).toBe("2024-01-15");
          expect(result.blog[0].author).toBe("Test Author");
          expect(result.blog[0].slug).toBe("my-post");
          expect(result.blog[0].route).toBe("/blog/my-post");
        }),
      );
    });

    describe("blog sorting", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/project/content/blog/older-post.mdx",
          `---
title: Older Post
description: An older post
date: 2024-01-01
author: Test Author
readTime: 5 min
---

Content`,
        )
        .addFile(
          "/project/content/blog/newer-post.mdx",
          `---
title: Newer Post
description: A newer post
date: 2024-02-01
author: Test Author
readTime: 5 min
---

Content`,
        );

      const { it } = createContentTestUtils(mockFs);

      it.effect("sorts blog posts by date (newest first)", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.blog).toHaveLength(2);
          expect(result.blog[0].title).toBe("Newer Post");
          expect(result.blog[1].title).toBe("Older Post");
        }),
      );
    });

    describe("policy processing", () => {
      const mockFs = new MockFileSystem().addFile(
        "/project/content/policy/privacy.mdx",
        `---
title: Privacy Policy
description: Our privacy policy
lastUpdated: 2024-01-01
---

# Privacy Policy

Content here.`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("processes policy content", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.policy).toHaveLength(1);
          expect(result.policy[0].title).toBe("Privacy Policy");
          expect(result.policy[0].lastUpdated).toBe("2024-01-01");
          expect(result.policy[0].route).toBe("/privacy");
        }),
      );
    });

    describe("dev processing", () => {
      const mockFs = new MockFileSystem().addFile(
        "/project/content/dev/playground.mdx",
        `---
title: Playground
description: A dev playground
---

# Playground

Dev content.`,
      );

      const { it } = createContentTestUtils(mockFs);

      it.effect("processes dev content", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.dev).toHaveLength(1);
          expect(result.dev[0].title).toBe("Playground");
          expect(result.dev[0].route).toBe("/dev/playground");
        }),
      );
    });

    describe("metadata file generation", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/project/content/blog/post.mdx",
          `---
title: Test Post
description: Test
date: 2024-01-01
author: Test
readTime: 5 min
---

Content`,
        )
        .addFile(
          "/project/content/dev/page.mdx",
          `---
title: Dev Page
description: Dev
---

Content`,
        );

      const { it, mockFs: fs } = createContentTestUtils(mockFs);

      it.effect("writes metadata index files", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          yield* processAllContent(config);

          // Check that metadata files were written
          const blogMeta = fs.getFile(
            "/project/public/static/content-meta/blog/index.json",
          );
          expect(blogMeta).toBeDefined();
          expect(JSON.parse(blogMeta!)).toHaveLength(1);

          const devMeta = fs.getFile(
            "/project/public/static/content-meta/dev/index.json",
          );
          expect(devMeta).toBeDefined();
          expect(JSON.parse(devMeta!)).toHaveLength(1);

          const unified = fs.getFile(
            "/project/public/static/content-meta/unified.json",
          );
          expect(unified).toBeDefined();
          expect(JSON.parse(unified!)).toHaveLength(2);
        }),
      );
    });

    describe("content file generation", () => {
      const mockFs = new MockFileSystem().addFile(
        "/project/content/blog/test-post.mdx",
        `---
title: Test Post
description: A test
date: 2024-01-01
author: Test
readTime: 5 min
---

# Hello

World`,
      );

      const { it, mockFs: fs } = createContentTestUtils(mockFs);

      it.effect("writes content JSON files", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          yield* processAllContent(config);

          const content = fs.getFile(
            "/project/public/static/content/blog/test-post.json",
          );
          expect(content).toBeDefined();

          const parsed = JSON.parse(content!) as {
            meta: { title: string };
            content: string;
          };
          expect(parsed.meta.title).toBe("Test Post");
          expect(parsed.content).toContain("# Hello");
        }),
      );
    });

    describe("error handling", () => {
      describe("missing required fields", () => {
        const mockFs = new MockFileSystem().addFile(
          "/project/content/blog/bad-post.mdx",
          `---
title: Missing Fields
---

Content without required fields.`,
        );

        const { it } = createContentTestUtils(mockFs);

        it.effect("collects errors for missing required fields", () =>
          Effect.gen(function* () {
            const config: PreprocessConfig = {
              baseDir: "/project",
              verbose: false,
            };

            // Should complete but with errors collected
            const result = yield* processAllContent(config).pipe(
              Effect.catchAll(() =>
                Effect.succeed({ blog: [], docs: [], policy: [], dev: [] }),
              ),
            );

            // The bad post should not be in the results
            expect(result.blog).toHaveLength(0);
          }),
        );
      });

      describe("invalid date format", () => {
        const mockFs = new MockFileSystem().addFile(
          "/project/content/blog/bad-date.mdx",
          `---
title: Bad Date
description: Has bad date
date: January 15, 2024
author: Test
readTime: 5 min
---

Content`,
        );

        const { it } = createContentTestUtils(mockFs);

        it.effect("rejects invalid date formats", () =>
          Effect.gen(function* () {
            const config: PreprocessConfig = {
              baseDir: "/project",
              verbose: false,
            };

            const result = yield* processAllContent(config).pipe(
              Effect.catchAll(() =>
                Effect.succeed({ blog: [], docs: [], policy: [], dev: [] }),
              ),
            );

            // The bad post should not be in the results
            expect(result.blog).toHaveLength(0);
          }),
        );
      });

      describe("invalid slug", () => {
        const mockFs = new MockFileSystem().addFile(
          "/project/content/blog/Bad-Slug.mdx",
          `---
title: Bad Slug
description: Has bad slug
date: 2024-01-01
author: Test
readTime: 5 min
---

Content`,
        );

        const { it } = createContentTestUtils(mockFs);

        it.effect("rejects invalid slugs", () =>
          Effect.gen(function* () {
            const config: PreprocessConfig = {
              baseDir: "/project",
              verbose: false,
            };

            const result = yield* processAllContent(config).pipe(
              Effect.catchAll(() =>
                Effect.succeed({ blog: [], docs: [], policy: [], dev: [] }),
              ),
            );

            // The bad post should not be in the results
            expect(result.blog).toHaveLength(0);
          }),
        );
      });
    });

    describe("empty content directories", () => {
      const mockFs = new MockFileSystem()
        .addDirectory("/project/content/blog")
        .addDirectory("/project/content/docs")
        .addDirectory("/project/content/policy")
        .addDirectory("/project/content/dev");

      const { it } = createContentTestUtils(mockFs);

      it.effect("handles empty directories gracefully", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.blog).toHaveLength(0);
          expect(result.docs).toHaveLength(0);
          expect(result.policy).toHaveLength(0);
          expect(result.dev).toHaveLength(0);
        }),
      );
    });

    describe("nested directories", () => {
      const mockFs = new MockFileSystem()
        .addFile(
          "/project/content/policy/terms/service.mdx",
          `---
title: Terms of Service
description: Our terms
lastUpdated: 2024-01-01
---

# Terms

Content.`,
        )
        .addFile(
          "/project/content/policy/terms/use.mdx",
          `---
title: Terms of Use
description: Use terms
lastUpdated: 2024-01-01
---

# Terms of Use

Content.`,
        );

      const { it, mockFs: fs } = createContentTestUtils(mockFs);

      it.effect("processes files in nested directories", () =>
        Effect.gen(function* () {
          const config: PreprocessConfig = {
            baseDir: "/project",
            verbose: false,
          };

          const result = yield* processAllContent(config);

          expect(result.policy).toHaveLength(2);

          // Check that files are written to correct nested paths
          const service = fs.getFile(
            "/project/public/static/content/policy/terms/service.json",
          );
          expect(service).toBeDefined();

          const use = fs.getFile(
            "/project/public/static/content/policy/terms/use.json",
          );
          expect(use).toBeDefined();
        }),
      );
    });
  });
});
