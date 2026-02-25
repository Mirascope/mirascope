import { createFileRoute } from "@tanstack/react-router";

import { CenteredLayout } from "@/app/components/centered-layout";
import { LoginPage } from "@/app/components/login-page";

export const Route = createFileRoute("/cloud/login")({
  component: () => (
    <CenteredLayout>
      <LoginPage />
    </CenteredLayout>
  ),
});
