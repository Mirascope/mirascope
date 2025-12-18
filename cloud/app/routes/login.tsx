import { CenteredLayout } from "@/app/components/centered-layout";
import { createFileRoute } from "@tanstack/react-router";
import { LoginPage } from "@/app/components/login-page";

export const Route = createFileRoute("/login")({
  component: () => (
    <CenteredLayout>
      <LoginPage />
    </CenteredLayout>
  ),
});
