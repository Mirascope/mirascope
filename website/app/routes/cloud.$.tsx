import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/cloud/$")({
  beforeLoad: () => {
    throw redirect({ to: "/cloud" });
  },
  component: () => null,
});
