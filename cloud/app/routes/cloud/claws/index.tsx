import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/cloud/claws/")({
  beforeLoad: () => {
    throw redirect({ to: "/cloud/claws/chat" });
  },
});
