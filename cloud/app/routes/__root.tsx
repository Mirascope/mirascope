/// <reference types="vite/client" />
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import {
  Outlet,
  createRootRoute,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { AuthProvider } from "@/app/contexts/auth";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/app/api/client";
import globalsCss from "@/app/styles/globals.css?url";
import { ThemeProvider } from "@/app/components/blocks/theme-provider";
import Header from "@/app/components/blocks/navigation/header";
import Footer from "@/app/components/blocks/navigation/footer";

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
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <Header />
              <main className="grow">
                {/* Content container with padding to account for fixed header */}
                <div className="mx-auto w-full max-w-7xl grow pt-(--header-height)">
                  <Outlet />
                </div>
              </main>
              <Footer />
              <TanStackRouterDevtools />
              <Scripts />
            </AuthProvider>
          </QueryClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
