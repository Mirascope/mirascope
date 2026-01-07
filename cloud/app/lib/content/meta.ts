// @ts-expect-error - virtual module resolved by vite plugin
import { blogPosts } from "virtual:content-meta";
import type { LoaderFnContext, AnyRoute } from "@tanstack/react-router";
import type { BlogContent, BlogMeta } from "@/app/lib/content/types";
import type { ProcessedMDX } from "@/app/lib/mdx/types";

export function getAllBlogMeta(): BlogMeta[] {
  return blogPosts as BlogMeta[];
}

/**
 * Function type for importing MDX modules.
 * Used for dependency injection in tests.
 */
export type MDXImporter = (
  slug: string,
) => Promise<{ mdx: ProcessedMDX } | undefined>;

/**
 * Default MDX importer using dynamic imports.
 * This is the production implementation.
 */
const defaultMDXImporter: MDXImporter = async (slug) => {
  return (await import(`@/content/blog/${slug}.mdx`)) as { mdx: ProcessedMDX };
};

// todo(sebastian): concrete prior to generic version
export async function blogPostContentLoader(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  context: LoaderFnContext<any, AnyRoute, any, { slug: string }>,
  /** Optional MDX importer for testing */
  importMDX: MDXImporter = defaultMDXImporter,
): Promise<BlogContent | undefined> {
  const { slug } = context.params;

  const blogPosts = getAllBlogMeta();

  // Validate slug to prevent path traversal attacks
  const meta = blogPosts.find((post) => post.slug === slug);
  if (!meta) {
    return undefined;
  }

  try {
    const module = await importMDX(slug);
    if (!module) {
      return undefined;
    }
    const { mdx } = module;
    const { content } = mdx;

    return <BlogContent>{
      meta,
      content,
      mdx,
    };
  } catch (err) {
    console.warn(`Error loading blog post ${slug}:`, err);
    return undefined;
  }
}
