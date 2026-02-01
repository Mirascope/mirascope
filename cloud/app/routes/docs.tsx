import { createFileRoute, Outlet } from "@tanstack/react-router";

import { TabbedSectionMemoryProvider } from "../components/blocks/tabbed-section-provider";

export const Route = createFileRoute("/docs")({
  component: DocsLayout,
});

function DocsLayout() {
  return (
    <div className="docs-layout">
      {/* This Outlet will render child routes like /docs/v1/placeholder */}
      {/* Eventually this will include sidebar, header, etc. */}
      <TabbedSectionMemoryProvider>
        <Outlet />
      </TabbedSectionMemoryProvider>
    </div>
  );
}
