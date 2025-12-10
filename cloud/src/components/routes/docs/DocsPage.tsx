import React from "react";
import {
  AppLayout,
  PageMeta,
  LoadingContent,
  ProviderContextProvider,
  useProduct,
} from "@/src/components";
import TocSidebar from "./TocSidebar";
import MainContent from "./MainContent";
import DocsSidebar from "./DocsSidebar";
import type { DocContent } from "@/src/lib/content";

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
  // Extract metadata for SEO (use defaults when loading)
  const meta = document?.meta || {
    title: "Loading...",
    description: "Loading documentation content",
  };
  const { title, description } = meta;
  const product = useProduct();

  return (
    <>
      <PageMeta
        title={title}
        description={description}
        product={product.name}
      />

      <ProviderContextProvider>
        <AppLayout>
          <AppLayout.LeftSidebar className="pt-1" collapsible={true}>
            <DocsSidebar product={product} />
          </AppLayout.LeftSidebar>

          <AppLayout.Content>
            {isLoading ? (
              <LoadingContent fullHeight={true} />
            ) : (
              document && <MainContent document={document} />
            )}
          </AppLayout.Content>

          <AppLayout.RightSidebar
            className="pt-1"
            mobileCollapsible={true}
            mobileTitle="On this page"
          >
            {isLoading ? (
              <div className="h-full">
                <div className="bg-muted mx-4 mt-16 h-6 animate-pulse rounded-md"></div>
              </div>
            ) : (
              document && <TocSidebar document={document} />
            )}
          </AppLayout.RightSidebar>
        </AppLayout>
      </ProviderContextProvider>
    </>
  );
};

export default DocsPage;
