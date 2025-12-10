/// <reference types="vite/client" />
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import {
  Outlet,
  createRootRoute,
  HeadContent,
  Scripts,
  useRouterState,
  redirect,
} from "@tanstack/react-router";
import { useEffect } from "react";
// Import providers directly to avoid circular dependencies through barrel exports
import { AuthProvider } from "@/src/components/core/providers/AuthContext";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/src/api/client";
import globalsCss from "@/src/styles/globals.css?url";

// Website imports
import { processRedirects } from "@/src/lib/redirects";
import { getProductFromPath, canonicalizePath } from "@/src/lib/utils";
import { Header, Footer, DevToolsButton } from "@/src/components/routes/root";
import analyticsManager from "@/src/lib/services/analytics";
// Import providers directly to avoid circular dependencies
import { FunModeProvider } from "@/src/components/core/providers/FunModeContext";
import { ThemeProvider } from "@/src/components/core/providers/ThemeContext";
import { ProductProvider } from "@/src/components/core/providers/ProductContext";
import { TabbedSectionMemoryProvider } from "@/src/components/core/providers/TabbedSectionMemoryContext";

export const Route = createRootRoute({
  beforeLoad: ({ location }) => {
    // Skip redirect logic for app routes (SSR)
    if (
      location.pathname.startsWith("/app") ||
      location.pathname.startsWith("/auth")
    ) {
      return;
    }

    const path = location.pathname;

    // Canonicalize the path by removing trailing slash
    const canonical = canonicalizePath(path);
    if (path !== canonical) {
      console.log(
        `Canonicalizing path by removing trailing slash: ${canonical}`,
      );
      if (typeof window !== "undefined") {
        window.history.replaceState(null, "", canonical);
      }
      throw redirect({
        to: canonical,
        replace: true,
      });
    }

    // Check if this is a path that needs redirection
    const redirectTo = processRedirects(path);
    if (redirectTo) {
      console.log(`Root redirect: ${path} -> ${redirectTo}`);
      throw redirect({
        to: redirectTo,
        replace: true,
      });
    }
  },
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
        href: "/apple-touch-icon.png",
      },
      {
        rel: "icon",
        type: "image/png",
        href: "/favicon.png",
      },
      { rel: "manifest", href: "/manifest.json" },
      { rel: "icon", href: "/favicon.ico" },
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

  // Determine which layout to use based on route
  const isAppRoute = path.startsWith("/app") || path.startsWith("/auth");
  const isLandingPage = ["/", "/router-waitlist"].includes(path);

  // Analytics tracking for website routes
  useEffect(() => {
    if (!isAppRoute) {
      analyticsManager.trackPageView(path);
    }
  }, [path, isAppRoute]);

  // Initialize analytics on first mount
  useEffect(() => {
    if (!isAppRoute) {
      analyticsManager.enableAnalytics();
    }
  }, [isAppRoute]);

  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            {isAppRoute ? (
              // App routes - minimal wrapper, SSR
              <>
                <Outlet />
                <TanStackRouterDevtools position="bottom-right" />
                <Scripts />
              </>
            ) : (
              // Website routes - full layout with providers, CSR
              <>
                {/* Fixed background for landing page */}
                {isLandingPage && <div className="watercolor-bg"></div>}

                <ThemeProvider>
                  <ProductProvider product={getProductFromPath(path)}>
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
                  </ProductProvider>

                  {/* Dev tools - only visible in development */}
                  <TanStackRouterDevtools />
                  <DevToolsButton className="fixed bottom-10 left-2 z-50" />
                </ThemeProvider>
                <Scripts />
              </>
            )}
          </AuthProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
