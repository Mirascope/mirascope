import { ChevronLeft } from "lucide-react";
import { ButtonLink } from "@/app/components/ui/button-link";
import { MDXRenderer } from "@/app/components/mdx/renderer";
import { CopyMarkdownButton } from "@/app/components/blocks/copy-markdown-button";
import LoadingContent from "@/app/components/blocks/loading-content";
import { ContentTOC } from "@/app/components/content-toc";
// import { PagefindMeta } from "@/app/components/pagefind-meta";
import type { BlogContent } from "@/app/lib/content/types";
import ContentLayout from "@/app/components/content-layout";
import { useEffect, useState } from "react";

// Reusable component for "Back to Blog" button
function BackToBlogLink() {
  return (
    <div className="flex justify-end">
      <ButtonLink href="/blog" variant="outline" size="sm">
        <ChevronLeft className="mr-1 h-4 w-4" />
        Back to Blog
      </ButtonLink>
    </div>
  );
}

type BlogPostPageProps = {
  post: BlogContent;
  slug: string;
  isLoading?: boolean;
};

export function BlogPostPage({
  post,
  slug,
  isLoading = false,
}: BlogPostPageProps) {
  // todo(sebastian): disabled - did this work before?
  const [, setOgImage] = useState<string | undefined>(undefined);

  // Find the first available image in the blog post directory
  useEffect(() => {
    if (isLoading) return;

    const findOgImage = async () => {
      try {
        const response = await fetch(`/assets/blog/${slug}/`);
        if (response.ok) {
          const text = await response.text();
          const parser = new DOMParser();
          const doc = parser.parseFromString(text, "text/html");
          const links = Array.from(doc.querySelectorAll("a"))
            .map((a) => a.getAttribute("href"))
            .filter((href) => href && /\.(png|jpg|jpeg|gif)$/i.test(href));

          if (links.length > 0) {
            setOgImage(`/assets/blog/${slug}/${links[0]}`);
          }
        }
      } catch (err) {
        console.error("Error finding OG image:", err);
      }
    };

    void findOgImage();
  }, [slug, isLoading]);

  // Extract metadata for easier access
  const { title, date, readTime, author, lastUpdated } = post.meta;

  // Main content
  const mainContent = isLoading ? (
    <LoadingContent className="min-w-0 flex-1" fullHeight={true} />
  ) : (
    <div className="min-w-0 flex-1 px-4">
      <div className="mx-auto max-w-5xl">
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
        <div id="blog-content" className="bg-background blog-content">
          {post.mdx ? (
            <MDXRenderer
              className="mdx-content overflow-y-auto"
              mdx={post.mdx}
            />
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )}
          {/* todo(sebastian): re-enable when PagefindMeta is implemented */}
          {/* {post.mdx ? (
            <PagefindMeta
              title={post.meta.title}
              description={post.meta.description}
              section={"blog"}
            >
                <MDXRenderer mdx={post.mdx} />
            </PagefindMeta>
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )} */}
        </div>
      </div>
    </div>
  );

  // Right sidebar content - loading state or actual content
  const rightSidebarContent = isLoading ? (
    <div className="h-full">
      <div className="bg-muted mx-4 mt-16 h-6 animate-pulse rounded-md"></div>
    </div>
  ) : (
    <div className="flex h-full flex-col">
      <div className="px-4 pt-4 lg:pt-0">
        <CopyMarkdownButton
          content={post.content}
          itemId={slug}
          contentType="blog_markdown"
        />

        <h4 className="text-muted-foreground mt-3 mb-3 text-sm font-medium">
          On this page
        </h4>
      </div>

      <div className="grow overflow-y-auto pr-4 pb-6 pl-4">
        {/* todo(sebastian): Make sure the headings have IDs in the mdx content */}
        <ContentTOC
          headings={post.mdx?.tableOfContents || []}
          observeHeadings={true}
        />
      </div>
    </div>
  );

  return (
    <>
      {/* <PageMeta
        title={title}
        description={post.meta.description || post.mdx?.frontmatter?.excerpt}
        image={ogImage}
        type="article"
        article={{
          publishedTime: date,
          modifiedTime: lastUpdated,
          author: author,
        }}
      /> */}
      <ContentLayout>
        <ContentLayout.LeftSidebar className="pt-1" collapsible={false}>
          <div className="pr-10">
            <BackToBlogLink />
          </div>
        </ContentLayout.LeftSidebar>

        <ContentLayout.Content>{mainContent}</ContentLayout.Content>

        <ContentLayout.RightSidebar
          className={isLoading ? undefined : "pt-1"}
          mobileCollapsible={true}
          mobileTitle="Table of Contents"
        >
          {rightSidebarContent}
        </ContentLayout.RightSidebar>
      </ContentLayout>
    </>
  );
}
