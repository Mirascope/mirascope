import React from "react";
import { Sidebar } from "@/src/components/core/layout";
import type { DevMeta } from "@/src/lib/content";
import type {
  SidebarConfig,
  SidebarItem,
} from "@/src/components/core/layout/Sidebar";

interface DevSidebarProps {
  devPages: DevMeta[];
}

/**
 * Convert DevMeta array to a SidebarConfig suitable for the Sidebar component
 */
function createDevSidebarConfig(devPages: DevMeta[]): SidebarConfig {
  // Create main section items
  const mainItems: Record<string, SidebarItem> = {
    index: {
      slug: "index",
      label: "Welcome",
      routePath: "/dev",
      hasContent: true,
    },
  };

  // Create interactive tools items
  const toolItems: Record<string, SidebarItem> = {
    "audit-metadata": {
      slug: "audit-metadata",
      label: "SEO Metadata Audit",
      routePath: "/dev/audit-metadata",
      hasContent: true,
    },
    "social-card": {
      slug: "social-card",
      label: "Social Card Preview",
      routePath: "/dev/social-card",
      hasContent: true,
    },
    "layout-test": {
      slug: "layout-test",
      label: "Layout Test",
      routePath: "/dev/layout-test",
      hasContent: true,
    },
  };

  // Create style test items from MDX pages
  const styleTestItems: Record<string, SidebarItem> = {};

  devPages.forEach((page) => {
    styleTestItems[page.slug] = {
      slug: page.slug,
      label: page.title,
      routePath: `/dev/${page.slug}`,
      hasContent: true,
    };
  });

  // Create a single section for dev content
  const devSection = {
    slug: "dev",
    label: "Developer",
    basePath: "/dev",
    items: mainItems,
    groups: {
      tools: {
        slug: "tools",
        label: "Tools",
        items: toolItems,
      },
      ...(Object.keys(styleTestItems).length > 0
        ? {
            "style-tests": {
              slug: "style-tests",
              label: "Style Tests",
              items: styleTestItems,
            },
          }
        : {}),
    },
  };

  // Return the complete sidebar config
  return {
    label: "Developer",
    sections: [devSection],
  };
}

const DevSidebar: React.FC<DevSidebarProps> = ({ devPages }) => {
  // Create sidebar configuration
  const sidebarConfig = createDevSidebarConfig(devPages);

  // Simple header content
  const headerContent = (
    <div className="mb-2 px-3">
      <span className="text-xl font-semibold">Developer Tools</span>
    </div>
  );

  return <Sidebar config={sidebarConfig} headerContent={headerContent} />;
};

export default DevSidebar;
