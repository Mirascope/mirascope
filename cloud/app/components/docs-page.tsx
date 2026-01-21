import React from "react";
import ContentLayout from "@/app/components/content-layout";
import { ModelProviderProvider } from "@/app/components/mdx/elements/model-provider-provider";
import DocsTocSidebar from "@/app/components/docs-toc-sidebar";
import MainContent from "@/app/components/blocks/docs/main-content";
import DocsSidebar from "@/app/components/docs-sidebar";
import type { DocContent } from "@/app/lib/content/types";

type DocsPageProps = {
  content: DocContent;
};

/**
 * DocsPage component - Top-level documentation page component
 *
 * Handles metadata, layout and content rendering for all documentation pages
 */
const DocsPage: React.FC<DocsPageProps> = ({ content }) => {
  return (
    <>
      <ModelProviderProvider>
        <ContentLayout>
          <ContentLayout.LeftSidebar className="pt-1" collapsible={true}>
            <DocsSidebar />
          </ContentLayout.LeftSidebar>

          <ContentLayout.Content>
            <MainContent document={content} />
          </ContentLayout.Content>

          <ContentLayout.RightSidebar
            className="pt-1"
            mobileCollapsible={true}
            mobileTitle="On this page"
          >
            <DocsTocSidebar document={content} />
          </ContentLayout.RightSidebar>
        </ContentLayout>
      </ModelProviderProvider>
    </>
  );
};

export default DocsPage;
