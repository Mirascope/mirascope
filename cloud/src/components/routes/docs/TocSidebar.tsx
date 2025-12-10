import React from "react";
import { TableOfContents } from "@/src/components/core/navigation";
import { Server } from "lucide-react";
import { ProviderDropdown } from "@/src/components/mdx/providers";
import { type DocContent } from "@/src/lib/content";
import { CopyMarkdownButton } from "@/src/components/ui/copy-markdown-button";

interface TocSidebarProps {
  document?: DocContent | null;
}

/**
 * TocSidebar - Right sidebar containing the table of contents and controls
 *
 * Displays provider selection dropdown and table of contents
 */
const TocSidebar: React.FC<TocSidebarProps> = ({ document }) => {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4">
        <div className="mb-4 flex flex-col gap-3">
          {document && (
            <CopyMarkdownButton
              content={document.content}
              itemId={document.meta.path}
              product={document.meta.product}
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
            <ProviderDropdown />
          </div>

          <h4 className="text-muted-foreground mt-4 text-sm font-medium">
            On this page
          </h4>
        </div>
        <TableOfContents
          headings={document?.mdx?.tableOfContents || []}
          observeHeadings={true}
        />
      </div>
    </div>
  );
};

export default TocSidebar;
