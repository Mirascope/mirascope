import React from "react";
import { useRouter } from "@tanstack/react-router";
import { ContentTOC } from "@/app/components/content-toc";
import { Server } from "lucide-react";
import { ModelProviderDropdown } from "@/app/components/mdx/elements/model-provider-dropdown";
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
  const router = useRouter();
  const currentPath = router.state.location.pathname;
  const isV1 = currentPath.startsWith("/docs/v1");

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

          {/* Provider dropdown - only shown in v1 docs where it's functional */}
          {isV1 && (
            <div className="mt-3">
              <h4 className="text-muted-foreground mb-2 text-sm font-medium">
                <div className="flex items-center">
                  <Server className="mr-1 h-3 w-3" />
                  Provider
                </div>
              </h4>
              <ModelProviderDropdown />
            </div>
          )}

          <h4 className="text-muted-foreground mt-4 text-sm font-medium">
            On this page
          </h4>
        </div>
        <ContentTOC
          headings={document?.mdx?.tableOfContents || []}
          observeHeadings={true}
        />
      </div>
    </div>
  );
};

export default DocsTocSidebar;
