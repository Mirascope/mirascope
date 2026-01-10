import React from "react";
import LoadingContent from "@/app/components/blocks/loading-content";
// import PagefindMeta from "@/app/components/blocks/pagefind-meta";
import { MDXRenderer } from "@/app/components/mdx/renderer";
import { type DocContent } from "@/app/lib/content/types";

interface MainContentProps {
  document: DocContent;
}

/**
 * MainContent - Main document content area
 *
 * Displays the document title, description, and rendered MDX content
 */
const MainContent: React.FC<MainContentProps> = ({ document }) => {
  // const path = document.meta.path;
  // const pieces = path.split("/");
  //   const section = pieces.slice(0, 3).join("/");
  return (
    <div className="px-2 lg:px-4">
      <div className="mx-auto w-full max-w-5xl">
        <div
          id="doc-content"
          className="prose prose-sm lg:prose-base prose-slate mdx-container max-w-none overflow-x-auto"
        >
          {document.mdx ? (
            <MDXRenderer className="mdx-content" mdx={document.mdx} />
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )}
          {/* {document.mdx ? (
            <PagefindMeta
              title={document.meta.title}
              description={document.meta.description}
              section={section}
            >
              <MDXRenderer
                code={document.mdx.code}
                frontmatter={document.mdx.frontmatter}
              />
            </PagefindMeta>
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )} */}
        </div>
      </div>
    </div>
  );
};

export default MainContent;
