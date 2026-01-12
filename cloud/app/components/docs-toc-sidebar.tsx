import React from "react";
import { PageTOC } from "@/app/components/page-toc";
import { Server } from "lucide-react";
import { ModelProviderDropdown } from "@/app/components/blocks/model-provider-dropdown";
import { type DocContent } from "@/app/lib/content/types";
import { CopyMarkdownButton } from "@/app/components/blocks/copy-markdown-button";

interface TocSidebarProps {
  document?: DocContent | null;
}

/**
 * DocsTocSidebar - Right sidebar containing the table of contents and controls
 *
 * Displays provider selection dropdown and table of contents
 */
const DocsTocSidebar: React.FC<TocSidebarProps> = ({ document }) => {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4">
        <div className="mb-4 flex flex-col gap-3">
          {document && (
            <CopyMarkdownButton
              content={document.content}
              itemId={document.meta.path}
              contentType="document_markdown"
            />
          )}

          {/* Provider dropdown */}
          <div className="mt-3">
            <h4 className="text-muted-foreground mb-2 text-sm font-medium">
              <div className="flex items-center">
                <Server className="mr-1 h-3 w-3" />
                Provider
              </div>
            </h4>
            <ModelProviderDropdown />
          </div>

          <h4 className="text-muted-foreground mt-4 text-sm font-medium">
            On this page
          </h4>
        </div>
        <PageTOC
          headings={document?.mdx?.tableOfContents || []}
          observeHeadings={true}
        />
      </div>
    </div>
  );
};

export default DocsTocSidebar;
