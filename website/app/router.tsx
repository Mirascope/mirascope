import { createRouter } from "@tanstack/react-router";

import { DefaultCatchBoundary } from "@/app/components/error/default-catch-boundary";
import { NotFound } from "@/app/components/not-found";
import { routeTree } from "@/app/routeTree.gen";

export function getRouter() {
  const router = createRouter({
    routeTree,
    defaultPreload: "intent",
    defaultErrorComponent: DefaultCatchBoundary,
    defaultNotFoundComponent: () => <NotFound />,
    scrollRestoration: true,
    // Configure scroll to top selectors to manage nested scrollable areas
    scrollToTopSelectors: [
      "#mdx-container", // Main MDX content container
    ],
  });

  return router;
}
