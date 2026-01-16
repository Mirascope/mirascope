import React from "react";
import LoadingContent from "@/app/components/blocks/loading-content";
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
  return (
    <div className="px-2 lg:px-4">
      <div className="mx-auto w-full max-w-5xl">
        <div
          id="doc-content"
          className="prose prose-sm lg:prose-base prose-slate mdx-container max-w-none overflow-x-auto"
        >
          {document.mdx ? (
            <MDXRenderer
              mdx={document.mdx}
              className="mdx-content"
              indexForSearch={true}
            />
          ) : (
            <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
          )}
        </div>
      </div>
    </div>
  );
};

export default MainContent;
