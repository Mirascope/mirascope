import { createFileRoute } from "@tanstack/react-router";
import { LoginPage } from "@/src/components/login-page";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});
