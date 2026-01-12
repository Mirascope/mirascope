import React from "react";
import PageLayout from "@/app/components/page-layout";
import LoadingContent from "@/app/components/blocks/loading-content";
import { ProviderContextProvider } from "@/app/components/blocks/model-provider-provider";
import DocsTocSidebar from "@/app/components/docs-toc-sidebar";
import MainContent from "@/app/components/blocks/docs/main-content";
import DocsSidebar from "@/app/components/blocks/docs/sidebar";
import type { DocContent } from "@/app/lib/content/types";

type DocsPageProps = {
  document?: DocContent;
  isLoading?: boolean;
};

/**
 * DocsPage component - Top-level documentation page component
 *
 * Handles metadata, layout and content rendering for all documentation pages
 * Supports both loaded and loading states
 */
const DocsPage: React.FC<DocsPageProps> = ({ document, isLoading = false }) => {
  return (
    <>
      <ProviderContextProvider>
        <PageLayout>
          <PageLayout.LeftSidebar className="pt-1" collapsible={true}>
            <DocsSidebar />
          </PageLayout.LeftSidebar>

          <PageLayout.Content>
            {isLoading ? (
              <LoadingContent fullHeight={true} />
            ) : (
              document && <MainContent document={document} />
            )}
          </PageLayout.Content>

          <PageLayout.RightSidebar
            className="pt-1"
            mobileCollapsible={true}
            mobileTitle="On this page"
          >
            {isLoading ? (
              <div className="h-full">
                <div className="bg-muted mx-4 mt-16 h-6 animate-pulse rounded-md"></div>
              </div>
            ) : (
              document && <DocsTocSidebar document={document} />
            )}
          </PageLayout.RightSidebar>
        </PageLayout>
      </ProviderContextProvider>
    </>
  );
};

export default DocsPage;
