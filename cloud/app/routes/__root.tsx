/// <reference types="vite/client" />
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import {
  Outlet,
  createRootRoute,
  HeadContent,
  Scripts,
  useRouterState,
} from "@tanstack/react-router";
import { AuthProvider } from "@/app/contexts/auth";
import { AnalyticsProvider } from "@/app/contexts/analytics";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/app/api/client";
import globalsCss from "@/app/styles/globals.css?url";
import {
  ThemeProvider,
  useIsLandingPage,
} from "@/app/components/blocks/theme-provider";
import Header from "@/app/components/blocks/navigation/header";
import Footer from "@/app/components/blocks/navigation/footer";
import { usePageView } from "@/app/hooks/use-page-view";
import { Toaster } from "@/app/components/ui/sonner";

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
  const isCloudRoute =
    currentPath === "/cloud" || currentPath.startsWith("/cloud/");
  const isLandingPage = useIsLandingPage();

  return (
    <div
      className={
        isLandingPage
          ? "relative h-screen overflow-hidden"
          : "flex min-h-screen flex-col"
      }
    >
      <Header />
      <div
        className={
          isCloudRoute
            ? "w-full grow pt-[60px]"
            : isLandingPage
              ? "w-full"
              : "mx-auto w-full max-w-7xl grow pt-(--header-height)"
        }
      >
        <main className="grow">
          <Outlet />
        </main>
      </div>
      {!isCloudRoute && (
        <div className={isLandingPage ? "fixed right-0 bottom-0 left-0" : ""}>
          <Footer />
        </div>
      )}
      <Toaster />
      <TanStackRouterDevtools />
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
                <AppContent />
              </AuthProvider>
            </AnalyticsProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
