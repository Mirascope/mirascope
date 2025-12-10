import { createRouter } from "@tanstack/react-router";
import { routeTree } from "@/src/routeTree.gen";
import { DefaultCatchBoundary } from "@/src/components/core";
import { NotFound } from "@/src/components/core";

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
