import { createFileRoute, Outlet } from "@tanstack/react-router";
import { ExternalLink, Loader2, Settings } from "lucide-react";
import { useEffect } from "react";

import { ClawHeader } from "@/app/components/claw-header";
import { Button } from "@/app/components/ui/button";
import { useClaw } from "@/app/contexts/claw";

function getGatewayUrl(orgSlug: string, clawSlug: string): string {
  if (typeof window === "undefined") return "#";
  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    const wsUrl = import.meta.env.VITE_OPENCLAW_GATEWAY_WS_URL;
    if (wsUrl) {
      return wsUrl.replace(/^wss:/, "https:").replace(/^ws:/, "http:");
    }
    return "http://localhost:18789/";
  }
  // Handle mirascope.dev (dev environment)
  if (hostname === "mirascope.dev") {
    return `https://openclaw.mirascope.dev/${orgSlug}/${clawSlug}/overview`;
  }
  const match = hostname.match(/^([\w-]+)\.(mirascope\.com)$/);
  const base =
    match && match[1] !== "www"
      ? `openclaw.${match[1]}.${match[2]}`
      : "openclaw.mirascope.com";
  return `https://${base}/${orgSlug}/${clawSlug}/overview`;
}

function ClawLayout() {
  const { clawSlug, orgSlug } = Route.useParams();
  const { claws, setSelectedClaw, isLoading } = useClaw();

  // Sync claw from URL slug
  useEffect(() => {
    if (isLoading) return;
    const claw = claws.find((c) => c.slug === clawSlug);
    if (claw) {
      setSelectedClaw(claw);
    }
  }, [clawSlug, claws, isLoading, setSelectedClaw]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const claw = claws.find((c) => c.slug === clawSlug);
  if (!claw) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Not Found</h1>
          <p className="text-muted-foreground mt-2">Claw not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex shrink-0 items-start justify-between px-6 pt-6">
        <ClawHeader />
        <div className="flex items-center gap-2">
          <Button asChild size="sm" variant="outline">
            <a href={`/settings/organizations/${orgSlug}/claws/${clawSlug}`}>
              <Settings className="mr-1.5 size-4" />
              Settings
            </a>
          </Button>
          <Button asChild size="sm" variant="default">
            <a
              href={getGatewayUrl(orgSlug, clawSlug)}
              rel="noopener noreferrer"
              target="_blank"
            >
              <ExternalLink className="mr-1.5 size-4" />
              OpenClaw Gateway
            </a>
          </Button>
        </div>
      </div>
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/$orgSlug/claws/$clawSlug")({
  component: ClawLayout,
});
