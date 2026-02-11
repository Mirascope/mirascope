import { Outlet, createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/dev")({
  component: DevLayout,
});

function DevLayout() {
  // The Outlet component renders the child route component
  return <Outlet />;
}
