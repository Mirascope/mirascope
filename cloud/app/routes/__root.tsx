import { QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRoute,
  HeadContent,
  Scripts,
  useRouterState,
} from "@tanstack/react-router";
/// <reference types="vite/client" />
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

import { queryClient } from "@/app/api/client";
import DevToolsButton from "@/app/components/blocks/dev/dev-tools-button";
import Footer from "@/app/components/blocks/navigation/footer";
import Header from "@/app/components/blocks/navigation/header";
import {
  ThemeProvider,
  useIsLandingPage,
  useIsLoginPage,
  useIsWatercolorPage,
} from "@/app/components/blocks/theme-provider";
import { Toaster } from "@/app/components/ui/sonner";
import { AnalyticsProvider } from "@/app/contexts/analytics";
import { AuthProvider } from "@/app/contexts/auth";
import { OrganizationProvider } from "@/app/contexts/organization";
import { usePageView } from "@/app/hooks/use-page-view";
import { isApplicationRoute } from "@/app/lib/route-utils";
import globalsCss from "@/app/styles/globals.css?url";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      {
        title: "Mirascope",
      },
    ],
    links: [
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      {
        rel: "preconnect",
        href: "https://fonts.gstatic.com",
        crossOrigin: "anonymous",
      },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Caveat:wght@400..700&family=Nunito:ital,wght@0,200..1000;1,200..1000&display=swap",
      },
      { rel: "stylesheet", href: globalsCss },
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "/icons/apple-touch-icon.png",
      },
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/icons/favicon-32x32.png",
      },
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/icons/favicon-16x16.png",
      },
      { rel: "manifest", href: "/manifest.json", color: "#fffff" },
      { rel: "icon", href: "/icons/favicon.ico" },
    ],
  }),
  component: RootComponent,
});

function AppContent() {
  usePageView();

  const router = useRouterState();
  const currentPath = router.location.pathname;
  const isAppRoute = isApplicationRoute(currentPath);
  const isDocsRoute =
    currentPath === "/docs" || currentPath.startsWith("/docs/");
  const isWatercolorPage = useIsWatercolorPage();
  const isLandingPage = useIsLandingPage();
  const isLoginPage = useIsLoginPage();
  const isFullBleedPage = isLandingPage || isLoginPage;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div
        className={
          isAppRoute
            ? "w-full grow pt-[60px]"
            : isFullBleedPage
              ? "flex w-full grow flex-col pt-(--header-height)"
              : isWatercolorPage
                ? "w-full grow pt-(--header-height)"
                : isDocsRoute
                  ? "mx-auto w-full max-w-7xl grow pt-(--header-height-with-selector)"
                  : "mx-auto w-full max-w-7xl grow pt-(--header-height)"
        }
      >
        <main className="flex grow flex-col">
          <Outlet />
        </main>
      </div>
      {!isAppRoute && <Footer />}
      <Toaster />
      <TanStackRouterDevtools />
      <DevToolsButton className="fixed bottom-10 left-2 z-50" />
      <Scripts />
    </div>
  );
}

function RootComponent() {
  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            <AnalyticsProvider>
              <AuthProvider>
                <OrganizationProvider>
                  <AppContent />
                </OrganizationProvider>
              </AuthProvider>
            </AnalyticsProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
