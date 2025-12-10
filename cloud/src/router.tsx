import { createRouter } from "@tanstack/react-router";
import { routeTree } from "@/src/routeTree.gen";
// Import directly to avoid circular dependency through barrel exports during SSR
import DefaultCatchBoundary from "@/src/components/core/error/DefaultCatchBoundary";
import NotFound from "@/src/components/core/error/NotFound";

export function getRouter() {
  const router = createRouter({
    routeTree,
    defaultPreload: "intent",
    defaultErrorComponent: DefaultCatchBoundary,
    defaultNotFoundComponent: () => <NotFound />,
    scrollRestoration: true,
  });

  return router;
}
