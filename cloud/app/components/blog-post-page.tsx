import { ChevronLeft } from "lucide-react";

import type { BlogContent } from "@/app/lib/content/types";

import { CopyMarkdownButton } from "@/app/components/blocks/copy-markdown-button";
import LoadingContent from "@/app/components/blocks/loading-content";
import { ContentTOC } from "@/app/components/content-toc";
import { MDXRenderer } from "@/app/components/mdx/renderer";
import { ButtonLink } from "@/app/components/ui/button-link";
import { WatercolorBackground } from "@/app/components/watercolor-background";
import { useSunsetTime } from "@/app/hooks/sunset-time";

type BlogPostPageProps = {
  content: BlogContent;
};

export function BlogPostPage({ content }: BlogPostPageProps) {
  useSunsetTime();

  const slug = content.meta.slug;
  const { title, date, readTime, author, lastUpdated } = content.meta;

  return (
    <>
      <WatercolorBackground />
      <div className="mx-auto flex w-full max-w-7xl gap-6 px-4 pt-4">
        {/* Left: Back button only */}
        <div className="hidden shrink-0 md:block">
          <div className="sticky top-[calc(var(--header-height)+1rem)]">
            <ButtonLink
              href="/blog"
              variant="outline"
              size="sm"
              className="border-white/30 bg-white/10 text-white backdrop-blur-sm hover:bg-white/20 hover:text-white dark:border-border/40 dark:bg-background/40"
            >
              <ChevronLeft className="mr-1 h-4 w-4" />
              Back to Blog
            </ButtonLink>
          </div>
        </div>

        {/* Center: Content card */}
        <div className="min-w-0 flex-1">
          <div className="rounded-xl border border-white/20 bg-white p-8 shadow-sm backdrop-blur-sm dark:border-border/40 dark:bg-black">
            {/* Mobile back button */}
            <div className="mb-4 md:hidden">
              <ButtonLink href="/blog" variant="outline" size="sm">
                <ChevronLeft className="mr-1 h-4 w-4" />
                Back to Blog
              </ButtonLink>
            </div>

            <div className="mb-6">
              <h1 className="mb-4 text-2xl font-semibold sm:text-3xl md:text-4xl">
                {title}
              </h1>
              <p className="text-muted-foreground text-sm sm:text-base">
                {date} · {readTime} · By {author}
              </p>
              {lastUpdated && (
                <p className="text-muted-foreground mt-1 text-sm italic sm:text-base">
                  Last updated: {lastUpdated}
                </p>
              )}
            </div>
            <div id="blog-content" className="blog-content">
              {content.mdx ? (
                <MDXRenderer
                  mdx={content.mdx}
                  className="mdx-content overflow-y-auto"
                />
              ) : (
                <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
              )}
            </div>
          </div>
        </div>

        {/* Right: ToC card (fit content, not full height) */}
        <div className="hidden w-56 shrink-0 lg:block">
          <div className="sticky top-[calc(var(--header-height)+1rem)] rounded-xl border border-white/20 bg-white/80 p-4 shadow-sm backdrop-blur-sm dark:border-border/40 dark:bg-background/80">
            <CopyMarkdownButton
              content={content.content}
              itemId={slug}
              contentType="blog_markdown"
            />

            <h4 className="text-muted-foreground mt-3 mb-3 text-sm font-medium">
              On this page
            </h4>

            <div className="max-h-[calc(100vh-20rem)] overflow-y-auto">
              <ContentTOC
                headings={content.mdx?.tableOfContents || []}
                observeHeadings={true}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
