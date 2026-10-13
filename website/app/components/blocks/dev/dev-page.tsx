import React from "react";

import { MDXRenderer } from "@/app/components/mdx/renderer";
import { type DevContent } from "@/app/lib/content/types";
import { getAllDevMeta } from "@/app/lib/content/virtual-module";

import DevLayout from "./dev-layout";

interface DevPageProps {
  content: DevContent;
}

/**
 * DevPage - Reusable component for rendering dev content pages
 */
const DevPage: React.FC<DevPageProps> = ({ content }) => {
  const devPages = getAllDevMeta();

  return (
    <DevLayout devPages={devPages}>
      <div className="mx-auto w-full">
        <div className="prose dark:prose-invert max-w-none">
          <MDXRenderer className="mdx-content" mdx={content.mdx} />
        </div>
      </div>
    </DevLayout>
  );
};

export default DevPage;
