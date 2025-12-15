import { createRouter } from "@tanstack/react-router";
import { routeTree } from "@/app/routeTree.gen";
import { DefaultCatchBoundary } from "@/app/components/error/default-catch-boundary";
import { NotFound } from "@/app/components/not-found";

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
