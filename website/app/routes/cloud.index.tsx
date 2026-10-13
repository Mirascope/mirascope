import { createFileRoute, Link } from "@tanstack/react-router";

import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

function CloudIndexRoute() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-6 py-24 text-center">
      <h1 className="mb-6 text-4xl font-bold tracking-tight">
        Mirascope Cloud Has Been Discontinued
      </h1>
      <p className="text-muted-foreground mb-4 max-w-2xl text-lg">
        We're sorry, but Mirascope Cloud is no longer available. We've made the
        decision to focus entirely on our open-source SDKs.
      </p>
      <p className="text-muted-foreground mb-8 max-w-2xl text-lg">
        The Mirascope <strong>Python</strong> and <strong>TypeScript</strong>{" "}
        SDKs remain fully supported and actively developed. For observability,
        our SDKs are built on{" "}
        <a
          href="https://opentelemetry.io/"
          className="text-primary underline underline-offset-4"
          target="_blank"
          rel="noopener noreferrer"
        >
          OpenTelemetry
        </a>
        , so you can use any OTEL-compatible backend such as{" "}
        <a
          href="https://langfuse.com"
          className="text-primary underline underline-offset-4"
          target="_blank"
          rel="noopener noreferrer"
        >
          Langfuse
        </a>
        , Jaeger, Grafana Tempo, Datadog, and more.
      </p>
      <div className="flex gap-4">
        <Link
          to="/docs"
          className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex items-center rounded-md px-6 py-3 text-sm font-medium transition-colors"
        >
          View Documentation
        </Link>
        <a
          href="https://github.com/Mirascope/mirascope"
          className="border-input bg-background hover:bg-accent hover:text-accent-foreground inline-flex items-center rounded-md border px-6 py-3 text-sm font-medium transition-colors"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </a>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/cloud/")({
  head: createStaticRouteHead("/cloud/"),
  component: CloudIndexRoute,
});
