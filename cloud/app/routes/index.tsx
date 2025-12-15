import type { ReactNode } from "react";

import { FrontPage } from "@/app/components/front-page";
import { Protected } from "@/app/components/protected";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: App,
});

// Centers content in the middle of the page.
const CenteredContent = ({ children }: { children: ReactNode }) => {
  return (
    <div className="w-full min-h-[calc(100vh-var(--header-height))] grid place-items-center p-8">
      {children}
    </div>
  );
};

function App() {
  return (
    <CenteredContent>
      <Protected>
        <FrontPage />
      </Protected>
    </CenteredContent>
  );
}
