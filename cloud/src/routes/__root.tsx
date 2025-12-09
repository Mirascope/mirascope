/// <reference types="vite/client" />
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import {
  Outlet,
  createRootRoute,
  HeadContent,
  Scripts,
  useRouterState,
} from "@tanstack/react-router";
import { useEffect } from "react";
import { AuthProvider } from "@/src/contexts/auth";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/src/api/client";
import globalsCss from "@/src/styles/globals.css?url";
import { Header, Footer, DevToolsButton } from "@/src/components/routes/root";
import {
  FunModeProvider,
  ThemeProvider,
  ProductProvider,
  TabbedSectionMemoryProvider,
  CoreMeta,
} from "@/src/components";
import { getProductFromPath } from "@/src/lib/utils";
import analyticsManager from "@/src/lib/services/analytics";

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
        title: "Mirascope Cloud",
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
      {
        rel: "preload",
        href: "/fonts/Williams-Handwriting-Regular-v1.ttf",
        as: "font",
        type: "font/ttf",
        crossOrigin: "anonymous",
      },
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  const router = useRouterState();
  const path = router.location.pathname;
  const isLandingPage = ["/home", "/router-waitlist"].includes(path);

  useEffect(() => {
    if (typeof window !== "undefined") {
      analyticsManager.trackPageView(path);
    }
  }, [path]);

  // Initialize analytics and set product on first mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      analyticsManager.enableAnalytics();
    }
  }, []);

  return (
    <html>
      <head>
        <HeadContent />
        <CoreMeta>
          <meta charSet="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        </CoreMeta>
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <ThemeProvider>
              <ProductProvider product={getProductFromPath(path)}>
                {/* Fixed background for landing page */}
                {isLandingPage && <div className="watercolor-bg"></div>}

                <div
                  className="flex min-h-screen flex-col px-2"
                  style={
                    {
                      "--header-height": path.startsWith("/docs/")
                        ? "var(--header-height-with-selector)"
                        : "var(--header-height-base)",
                    } as React.CSSProperties
                  }
                >
                  {/* Header is fixed, so it's outside the content flow */}
                  <Header showProductSelector={path.startsWith("/docs/")} />

                  {/* Content container with padding to account for fixed header */}
                  <div
                    className="mx-auto w-full max-w-7xl flex-grow"
                    style={{ paddingTop: "var(--header-height)" }}
                  >
                    <FunModeProvider>
                      <TabbedSectionMemoryProvider>
                        <main className="flex-grow">
                          <Outlet />
                        </main>
                      </TabbedSectionMemoryProvider>
                    </FunModeProvider>
                  </div>
                  <Footer />
                </div>

                {/* Dev tools - only visible in development */}
                <TanStackRouterDevtools position="bottom-right" />
                <DevToolsButton className="fixed bottom-10 left-2 z-50" />
              </ProductProvider>
            </ThemeProvider>
          </AuthProvider>
        </QueryClientProvider>
        <Scripts />
      </body>
    </html>
  );
}
