import React from "react";

import type { DevMeta } from "@/app/lib/content/types";

import ContentLayout from "@/app/components/content-layout";

import DevSidebar from "./dev-sidebar";

interface DevLayoutProps {
  children: React.ReactNode;
  devPages: DevMeta[];
}

/**
 * DevLayout - Page component for developer tools section
 *
 * Provides a consistent layout for all dev tool pages with responsive sidebar
 */
const DevLayout: React.FC<DevLayoutProps> = ({ children, devPages }) => {
  return (
    <ContentLayout>
      <ContentLayout.LeftSidebar>
        <DevSidebar devPages={devPages} />
      </ContentLayout.LeftSidebar>

      <ContentLayout.Content>
        <div className="max-w-5xl px-8">{children}</div>
      </ContentLayout.Content>
    </ContentLayout>
  );
};

export default DevLayout;
