import { createFileRoute, Outlet } from "@tanstack/react-router";

function CloudLayout() {
  return <Outlet />;
}

export const Route = createFileRoute("/cloud")({
  component: CloudLayout,
});
