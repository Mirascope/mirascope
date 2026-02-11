import { createFileRoute, Navigate } from "@tanstack/react-router";

function ClawIndexRedirect() {
  const { orgSlug, clawSlug } = Route.useParams();
  return (
    <Navigate
      to="/$orgSlug/claws/$clawSlug/chat"
      params={{ orgSlug, clawSlug }}
      replace
    />
  );
}

export const Route = createFileRoute("/$orgSlug/claws/$clawSlug/")({
  component: ClawIndexRedirect,
});
