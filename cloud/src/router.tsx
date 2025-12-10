import { createRouter } from "@tanstack/react-router";
import { DefaultCatchBoundary } from "@/src/components/default-catch-boundary";
import { NotFound } from "@/src/components/not-found";

let routerInstance: ReturnType<typeof createRouter> | null = null;
let routeTreeModule: typeof import("@/src/routeTree.gen") | null = null;

// Lazy load routeTree to avoid circular dependency
async function getRouteTree() {
  if (!routeTreeModule) {
    routeTreeModule = await import("@/src/routeTree.gen");
  }
  return routeTreeModule.routeTree;
}

export async function getRouter() {
  if (routerInstance) {
    return routerInstance;
  }

  const routeTree = await getRouteTree();

  routerInstance = createRouter({
    routeTree,
    defaultPreload: "intent",
    defaultErrorComponent: DefaultCatchBoundary,
    defaultNotFoundComponent: () => <NotFound />,
    scrollRestoration: true,
  });

  return routerInstance;
}
