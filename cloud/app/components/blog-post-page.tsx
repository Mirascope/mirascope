import { ChevronLeft } from "lucide-react";
import { ButtonLink } from "@/app/components/ui/button-link";
import { MDXRenderer } from "@/app/components/mdx/renderer";
import { CopyMarkdownButton } from "@/app/components/blocks/copy-markdown-button";
import LoadingContent from "@/app/components/blocks/loading-content";
import { ContentTOC } from "@/app/components/content-toc";
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
  content: BlogContent;
};

export function BlogPostPage({ content }: BlogPostPageProps) {
  const slug = content.meta.slug;

  // todo(sebastian): disabled - did this work before?
  const [, setOgImage] = useState<string | undefined>(undefined);

  // Find the first available image in the blog post directory
  useEffect(() => {
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
  }, [slug]);

  // Extract metadata for easier access
  const { title, date, readTime, author, lastUpdated } = content.meta;

  // Main content
  const mainContent = (
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
          {content.mdx ? (
            <MDXRenderer
              className="mdx-content overflow-y-auto"
              mdx={content.mdx}
            />
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )}
        </div>
      </div>
    </div>
  );

  // Right sidebar content
  const rightSidebarContent = (
    <div className="flex h-full flex-col">
      <div className="px-4 pt-4 lg:pt-0">
        <CopyMarkdownButton
          content={content.content}
          itemId={slug}
          contentType="blog_markdown"
        />

        <h4 className="text-muted-foreground mt-3 mb-3 text-sm font-medium">
          On this page
        </h4>
      </div>

      <div className="grow overflow-y-auto pr-4 pb-6 pl-4">
        <ContentTOC
          headings={content.mdx?.tableOfContents || []}
          observeHeadings={true}
        />
      </div>
    </div>
  );

  return (
    <>
      <ContentLayout>
        <ContentLayout.LeftSidebar className="pt-1" collapsible={false}>
          <div className="pr-10">
            <BackToBlogLink />
          </div>
        </ContentLayout.LeftSidebar>

        <ContentLayout.Content>{mainContent}</ContentLayout.Content>

        <ContentLayout.RightSidebar
          className="pt-1"
          mobileCollapsible={true}
          mobileTitle="Table of Contents"
        >
          {rightSidebarContent}
        </ContentLayout.RightSidebar>
      </ContentLayout>
    </>
  );
}
