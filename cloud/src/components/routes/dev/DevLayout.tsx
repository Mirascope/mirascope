import React from "react";
import DevSidebar from "./DevSidebar";
import { AppLayout } from "@/src/components/core/layout";
import type { DevMeta } from "@/src/lib/content";

interface DevLayoutProps {
  children: React.ReactNode;
  devPages: DevMeta[];
}

/**
 * DevLayout - Layout component for developer tools section
 *
 * Provides a consistent layout for all dev tool pages with responsive sidebar
 */
const DevLayout: React.FC<DevLayoutProps> = ({ children, devPages }) => {
  return (
    <AppLayout>
      <AppLayout.LeftSidebar>
        <DevSidebar devPages={devPages} />
      </AppLayout.LeftSidebar>

      <AppLayout.Content>
        <div className="max-w-5xl px-8">{children}</div>
      </AppLayout.Content>
    </AppLayout>
  );
};

export default DevLayout;
